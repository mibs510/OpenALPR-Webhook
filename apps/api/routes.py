from apps.api import blueprint
from apps.api.controller.webhook_controller import Webhook
from flask_restx import Api


# from flask_restx import Api
api = Api(blueprint, title="OpenALPR-Webhook", description="OpenALPR-Webhook is a self-hosted web application"
                                                           " that accepts Rekor Scout™ POST data allowing longer "
                                                           "data retention.")

# ALPR Group/Alert & Vehicle POST end point.
api.add_resource(Webhook, '/webhook')
