import logging
import socket

from worker_manager_enums import WMSCommand, WMSResponse


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
