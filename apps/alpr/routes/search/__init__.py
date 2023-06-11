from flask import Blueprint

blueprint = Blueprint(
    'search',
    __name__,
    url_prefix='/search'
)
