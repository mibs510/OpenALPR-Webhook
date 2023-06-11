from flask import Blueprint

blueprint = Blueprint(
    'alerts',
    __name__,
    url_prefix='/alerts'
)
