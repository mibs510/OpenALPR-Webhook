#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import argparse
import logging
import multiprocessing
import os
import platform
import signal
import socket
import sys
import time

import redis as redis
from progressbar import progressbar
from redis import Redis
from rq import Worker
from rq.command import send_kill_horse_command
from rq.worker import WorkerStatus
from setproctitle import setproctitle

import log
from apps import helpers
from worker_manager_enums import WMSCommand, WorkerType, WMSResponse

# Globals
worker_pids = {}
redis = redis.Redis()
parser = argparse.ArgumentParser("Redis/RQ-Python Worker Manager Server")
args = parser.parse_args()


def worker(_id, worker_type):
    from rq import Connection, Worker
    import os

    from apps.config import config_dict

    # WARNING: Don't run with debug turned on in production!
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # The configuration
    get_config_mode = 'Debug' if DEBUG else 'Production'

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

    # Default queue name and worker name
    _name = "Agent Worker ID: {}".format(str(_id[-4:]).upper())
    _queues = [WorkerType.General.value]

    if worker_type == WorkerType.Camera.value:
        _name = "Camera Worker ID: {}".format(_id)
        _queues = [_id]

    with Connection(connection=Redis()):
        _worker = Worker(queues=_queues, name=_name)
        _worker.work(with_scheduler=True)


def main() -> None:
    if platform.system() == "Windows":
        sys.exit("Redis cannot fork on Windows! Only on *nix!")

    # Change process title/name
    setproctitle("Worker Manager Server")

    # Logging
    log.init("WMS.log")

    # Flush any stale jobs and workers
    redis.flushall()
    redis.flushdb()

    try:
        time_wait = helpers.netstat()
        if time_wait != 0:
            logging.debug("time_wait = {}".format(round(time_wait + 1)))
            for i in progressbar(range(round(time_wait + 1)), redirect_stdout=True):
                time.sleep(0.7)
    except Exception as ex:
        logging.exception(ex)

    try:
        server = socket.socket()
        server.bind(('localhost', 3565))
        logging.info("Worker Manager Server started...")
    except OSError as ex:
        # TCP socket is probably in close CLOSE_WAIT state. Wait at lest 4 minutes before reattempting to rebind.
        logging.warning("Could not bind. Sleeping for 5 minutes before reattempting...")
        time.sleep(300)
        logging.info("Attempting to re-bind...")
        try:
            server = socket.socket()
            server.bind(('localhost', 3565))
            logging.info("Worker Manager Server started...")
        except OSError:
            logging.exception("Could not rebind! Exiting...")
            sys.exit(1)

    # Set the maximum connections to 2
    server.listen(2)

    running = True
    while running:
        connection, address = server.accept()
        logging.info("Connection accepted from {}:{}".format(address[0], address[1]))
        while True:
            message = connection.recv(1024).decode()

            if not message:
                break

            logging.debug("Received: {}".format(message))

            if WMSCommand.ACK.value == message:
                connection.send(WMSCommand.ACK.value.encode())

            if WMSCommand.CLOSE_CONNECTION.value == message:
                connection.close()

            if WMSCommand.STOP_ALL.value == message:
                try:

                    for _id, pid in worker_pids.items():
                        logging.info("Killing {} worker (PID: {})...".format(_id, pid))
                        os.kill(pid, signal.SIGINT)

                    workers = Worker.all(Redis())
                    for w in workers:
                        if w.get_state() == WorkerStatus.BUSY:
                            send_kill_horse_command(redis, w.name)

                    # Flush any stale jobs and workers
                    redis.flushall()
                    redis.flushdb()

                    connection.send(WMSResponse.SUCCESS.value.encode())
                    logging.info("PIDS: {}".format(worker_pids))
                except Exception as ex:
                    logging.exception(ex)
                    # White space delimiter will not work on the receiving end since `ex` will hold a lot of what spaces
                    # "exception~<Exception>"
                    connection.send(bytes(WMSResponse.EXCEPTION.value + WMSResponse.EXCEPTION_DELIMITER.value + ex))

            if WMSCommand.STOP_SERVER.value == message:
                logging.info("Stopping server...")

                # Flush any stale jobs and workers
                redis.flushall()
                redis.flushdb()

                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                sys.exit()

            # These commands have arguments seperated by whitespaces
            message = message.split(' ')

            if message[0] == WMSCommand.START_WORKER.value:
                try:
                    # message = ['start-worker', 'WorkerType', 'ID']
                    worker_type = WorkerType.General.value
                    if message[1] == WorkerType.Camera.value:
                        worker_type = WorkerType.Camera.value

                    worker_name = message[2]

                    # Kill the worker if it's alive
                    if worker_name in worker_pids.items():
                        logging.info("Killing {} worker with PID: {}...".format(worker_name, worker_pids[worker_name]))
                        os.kill(worker_pids[worker_name], signal.SIGINT)
                        worker_pids.pop(worker_name)

                    p = multiprocessing.Process(target=worker, args=(worker_name, worker_type,))
                    p.start()
                    worker_pids[worker_name] = p.pid
                    logging.info("Worker {} started with PID: {}".format(worker_name, worker_pids[worker_name]))

                    logging.info("PIDS: {}".format(worker_pids))
                    connection.send(WMSResponse.SUCCESS.value.encode())
                except Exception as ex:
                    logging.exception(ex)
                    # White space delimiter will not work on the receiving end since `ex` will hold a lot of what spaces
                    # "exception~<Exception>"
                    connection.send(bytes(WMSResponse.EXCEPTION.value + WMSResponse.EXCEPTION_DELIMITER.value +
                                          str(ex)))

            if message[0] == WMSCommand.STOP_WORKER.value:
                try:
                    # message = ['stop-worker', 'ID']
                    worker_name = message[1]

                    # Kill the worker if it's alive
                    if worker_name in worker_pids.keys():
                        logging.info("Killing {} worker (PID: {})...".format(worker_name, worker_pids[worker_name]))
                        # SIGINT is the equivalent of using rq.command.send_shutdown_command()
                        os.kill(worker_pids[worker_name], signal.SIGINT)

                        workers = Worker.all(Redis())
                        for w in workers:
                            if worker_name in w.name:
                                if w.get_state() == WorkerStatus.BUSY:
                                    logging.debug("Calling send_kill_horse_command(redis, {})...".format(w.name))
                                    send_kill_horse_command(redis, w.name)

                        worker_pids.pop(worker_name)

                    logging.info("PIDS: {}".format(worker_pids))
                    connection.send(WMSResponse.SUCCESS.value.encode())
                except Exception as ex:
                    logging.exception(ex)
                    # White space delimiter will not work on the receiving end since `ex` will hold a lot of what spaces
                    # "exception~<Exception>"
                    connection.send(bytes(WMSResponse.EXCEPTION.value + WMSResponse.EXCEPTION_DELIMITER.value + ex))
    server.close()
    server.detach()


if __name__ == "__main__":
    main()
