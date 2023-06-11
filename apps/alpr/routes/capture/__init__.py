from flask import Blueprint

blueprint = Blueprint(
    'capture',
    __name__,
    url_prefix='/capture'
)
