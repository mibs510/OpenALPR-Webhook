from flask import Blueprint

blueprint = Blueprint(
    'agents',
    __name__,
    url_prefix='/settings/agents'
)
