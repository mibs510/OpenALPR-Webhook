import enum


class AccountStatus(enum.Enum):
    NON_ACTIVATED = 0
    ACTIVATED = 1


class AccountVerified(enum.Enum):
    NON_VERIFIED = 0
    VERIFIED = 1


class ChartType(enum.Enum):
    ALERT_CHART = "alert-chart"
    CUSTOM_ALERT = "custom-alert"
    PLATES_CAPTURED_CHART = "plates-captured-chart"
    TOP_SECOND_REGION_CHART = "top-second-region-chart"


class DataType(enum.Enum):
    ALERT = "alpr_alert"
    GROUP = "alpr_group"
    VEHICLE = "vehicle"


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    REGULAR = "NONADMIN"



