from flask import Blueprint

blueprint = Blueprint(
    'alpr_alerts',
    __name__,
    url_prefix='/alerts/rekor'
)
