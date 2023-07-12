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

import logging
import os
import socket

from worker_manager_enums import WMSCommand, WMSResponse

# Used to launch Worker Manager Server
python3 = os.path.abspath(os.path.dirname(__file__)) + "/venv/bin/python3"


class WorkerManager:
    debug = False
    command = None
    _connected = False
    worker_id = None
    worker_type = None

    def __init__(self, command: WMSCommand):
        self.command = command

    def last_connection(self) -> bool:
        return self._connected

    def send(self) -> str:
        if self.worker_id is None:
            if self.command == WMSCommand.START_WORKER or self.command == WMSCommand.STOP_WORKER:
                raise Exception("worker_id cannot be type None")

        if self.command == WMSCommand.START_WORKER:
            if self.worker_type is None:
                raise Exception("worker_type cannot be type None")

        send = self.command.value

        if self.command == WMSCommand.START_WORKER:
            # server.recv() = "start-worker WorkerType ID"
            send = self.command.value + " " + self.worker_type.value + " " + str(self.worker_id)
        elif self.command == WMSCommand.STOP_WORKER:
            # server.recv() = "stop-worker ID"
            send = self.command.value + " " + str(self.worker_id)

        if self.debug:
            logging.debug("Sending: {}".format(send))
        send = send.encode()

        client = socket.socket()
        client.settimeout(5)

        try:
            client.connect(('localhost', 3565))
            self._connected = True
        except ConnectionRefusedError:
            Exception("Connection to Worker Manager Server refused. Please try again in 5 minutes?")

        try:
            client.send(send)
            response = client.recv(2048).decode()
        except TimeoutError:
            raise TimeoutError

        client.close()

        response_split = response.split(WMSResponse.EXCEPTION_DELIMITER.value)

        if self.debug:
            logging.debug("Response: {}".format(response))

        if response_split[0] == WMSResponse.EXCEPTION.value:
            logging.exception("Exception thrown by Worker Manager Server")
            raise Exception(response[1])
        else:
            return response
