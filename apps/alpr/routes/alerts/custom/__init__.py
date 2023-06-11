from flask import Blueprint

blueprint = Blueprint(
    'custom_alerts',
    __name__,
    url_prefix='/alerts/custom'
)
