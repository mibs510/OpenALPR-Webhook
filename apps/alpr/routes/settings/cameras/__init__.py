from flask import Blueprint

blueprint = Blueprint(
    'cameras',
    __name__,
    url_prefix='/settings/cameras'
)
