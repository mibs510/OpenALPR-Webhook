import enum


class WMSCommand(enum.Enum):
    ACK = "ack"
    CLOSE_CONNECTION = "close"
    START_WORKER = "start-worker"
    STOP_ALL = "stop-all"
    STOP_SERVER = "stop-server"
    STOP_WORKER = "stop-worker"


class WMSResponse(enum.Enum):
    EXCEPTION = "exception"
    # White space delimiter will not work on the receiving end since `ex` will hold a lot of what spaces
    # "exception~<Exception>"
    EXCEPTION_DELIMITER = "~"
    FAIL = "false"
    SUCCESS = "success"


class WorkerType(enum.Enum):
    # worker type = queue name
    Camera = 'camera'
    General = 'default'
