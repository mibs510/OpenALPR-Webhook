#!/usr/bin/env python
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
    import base64
    import logging
    import os
    import shutil
    import time
    from pathlib import Path

    import requests

    from apps.alpr.models.alpr_alert import ALPRAlert
    from apps.alpr.models.alpr_group import ALPRGroup
    from apps.alpr.enums import DataType
    from apps.alpr.models.custom_alert import CustomAlert
    from apps.alpr.models.settings import AgentSettings, EmailNotificationSettings, CameraSettings, GeneralSettings
    from apps.alpr.models.vehicle import Vehicle
    from apps.alpr.notify import Email, SMS, Tag
    from apps.alpr.routes.settings.cameras.manufacturers.Dahua import Dahua
    from apps.authentication.models import User, UserProfile
    from apps.authentication.routes import download_folder_name
    import apps.helpers as helper

    from apps import create_app
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
            logging.debug("time_wait = {}".format(time_wait))
            with progressbar(range(int(time_wait)), redirect_stdout=True):
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
