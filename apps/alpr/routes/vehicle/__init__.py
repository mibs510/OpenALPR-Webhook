from flask import Blueprint

blueprint = Blueprint(
    'vehicle',
    __name__,
    url_prefix='/vehicle'
)
