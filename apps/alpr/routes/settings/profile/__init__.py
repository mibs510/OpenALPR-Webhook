from flask import Blueprint

blueprint = Blueprint(
    'profile',
    __name__,
    url_prefix='/settings/profile'
)
