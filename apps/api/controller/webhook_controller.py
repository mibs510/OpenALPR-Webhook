import json
import logging

from flask import request
from flask_restx import Resource

from apps.alpr.enums import DataType
from apps.alpr.models.settings import GeneralSettings, PostAuth
from apps.authentication.models import User, RoleType
from apps.messages import Messages

from apps.api.controller.base_controller import BaseController

from apps.api.schemas.alpr_alert_schema import ALPRAlertSchema
from apps.api.schemas.alpr_group_schema import ALPRGroupSchema
from apps.api.schemas.vehicle_schema import VehicleSchema

from apps.api.service.alpr_alert_service import ALPRAlertService
from apps.api.service.alpr_group_service import ALPRGroupService
from apps.api.service.cache_service import CacheService
from apps.api.service.vehicle_service import VehicleService

message = Messages.message

# Base controller
BaseController = BaseController()

# Schemas
alpr_alert_schema = ALPRAlertSchema()
alpr_alerts_schema = ALPRAlertSchema(many=True)
alpr_group_schema = ALPRGroupSchema()
alpr_groups_schema = ALPRGroupSchema(many=True)
vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)

# Services
alpr_alert_service = ALPRAlertService()
alpr_group_service = ALPRGroupService()
vehicle_service = VehicleService()


class Webhook(Resource):
    def post(self):
        # Add security check. We do not want any unauthorized POSTing of data
        settings = GeneralSettings.get_settings()
        auth_level = settings.post_auth

        if request.is_json:
            if auth_level == PostAuth.DISABLE_POSTING:
                return BaseController.errorGeneral("POST has been disabled"), 403
            elif auth_level == PostAuth.USERS_ADMINS or auth_level == PostAuth.ADMINS_ONLY:
                try:
                    # Re-serialize the object "custom_data": "{\"API_KEY\": \"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\"}" ->
                    # "custom_data": {"API_KEY": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}
                    json_obj = json.loads(request.json['custom_data'])

                    api_key = json_obj['API_KEY']
                    if api_key != "":
                        token_holder = User.find_by_api_token(api_key)
                        if token_holder is None:
                            return BaseController.errorGeneral("Unknown API_KEY holder"), 403
                    else:
                        return BaseController.errorGeneral("Missing API_KEY in custom_data"), 403

                    if auth_level == PostAuth.ADMINS_ONLY:
                        if token_holder.role != RoleType['ADMIN']:
                            return BaseController.errorGeneral("API_KEY does not belong to an administrator"), 403

                except KeyError as ex:
                    logging.error("Could not process custom_data")
                    return BaseController.errorGeneral("Could not process custom_data")

                # Redefine custom_data for the schema validators
                request.json['custom_data'] = json_obj

            # Enumerate the 'data_type' key
            data_type = DataType(request.json['data_type'])

            if data_type == DataType.GROUP:
                try:
                    request_data = request.json
                    # Make sure incoming data conforms
                    validated = alpr_group_schema.load(request_data)
                    # Insert the record into the database and save it
                    record = alpr_group_service.create(validated)
                    # Return the data inserted back to client as an ack
                    data = alpr_group_schema.dump(record)
                    # Update cache
                    cache_service = CacheService(request_data, record.id)
                    cache_service.update()
                    return BaseController.success(data, message['record_created_successfully'])
                except Exception as e:
                    logging.exception(e)
                    return BaseController.error(e, 422)
            elif data_type == DataType.ALERT:
                try:
                    request_data = request.json
                    # Make sure incoming data conforms
                    validated = alpr_alert_schema.load(request_data)
                    # Insert the record into the database and save it
                    record = alpr_alert_service.create(validated)
                    # Return the data inserted back to client as an ack
                    data = alpr_alert_schema.dump(record)
                    # Update cache
                    cache_service = CacheService(request_data, record.id)
                    cache_service.update()
                    return BaseController.success(data, message['record_created_successfully'])
                except Exception as e:
                    logging.exception(e)
                    return BaseController.error(e, 422)
            elif data_type == DataType.VEHICLE:
                try:
                    request_data = request.json
                    # Make sure incoming data conforms
                    validated = vehicle_schema.load(request_data)
                    # Insert the record into the database and save it
                    record = vehicle_service.create(validated)
                    # Return the data inserted back to client as an ack
                    data = vehicle_schema.dump(record)
                    # Update cache
                    cache_service = CacheService(request_data, record.id)
                    cache_service.update()
                    return BaseController.success(data, message['record_created_successfully'])
                except Exception as e:
                    logging.exception(e)
                    return BaseController.error(e, 422)
            else:
                logging.error("data_type = {} is not valid".format(request.json['data_type']))
                return BaseController.errorGeneral("data_type not valid")
        else:
            logging.exception("Content type is not application/json?")
            return BaseController.errorGeneral("Content type is not application/json?")
