from flask import Blueprint

blueprint = Blueprint(
    'notifications',
    __name__,
    url_prefix='/settings/notifications'
)
