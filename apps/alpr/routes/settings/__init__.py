from flask import Blueprint

blueprint = Blueprint(
    'settings',
    __name__,
    url_prefix='/settings'
)
