from flask import Blueprint

blueprint = Blueprint(
    'maintenance',
    __name__,
    url_prefix='/settings/maintenance'
)
