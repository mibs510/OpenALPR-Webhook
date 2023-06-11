from flask import Blueprint

blueprint = Blueprint(
    "rq_dashboard",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix='/settings/maintenance/queue'
)
