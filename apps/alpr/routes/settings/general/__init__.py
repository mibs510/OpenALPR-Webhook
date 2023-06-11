from flask import Blueprint

blueprint = Blueprint(
    'general',
    __name__,
    url_prefix='/settings/general'
)
