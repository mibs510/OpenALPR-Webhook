from flask import Blueprint

blueprint = Blueprint(
    'alert',
    __name__,
    url_prefix='/alert'
)
