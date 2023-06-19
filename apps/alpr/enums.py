import enum


class AccountStatus(enum.Enum):
    NON_ACTIVATED = 0
    ACTIVATED = 1


class AccountVerified(enum.Enum):
    NON_VERIFIED = 0
    VERIFIED = 1


class ChartType(enum.Enum):
    ALERT_CHART = "alert-chart"
    PLATES_CAPTURED_CHART = "plates-captured-chart"
    TOP_REGION_CHART = "top-region-chart"


class DataType(enum.Enum):
    ALERT = "alpr_alert"
    GROUP = "alpr_group"
    VEHICLE = "vehicle"


class MultiProcessCommand(enum.Enum):
    START_WORKER = "start-worker"
    STOP_WORKER = "stop-worker"
    CLOSE_CONNECTION = "close"


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    REGULAR = "NONADMIN"


class WorkerType(enum.Enum):
    # worker type = queue name
    Camera = 'cameras'
    General = 'default'
