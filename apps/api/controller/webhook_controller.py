#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
                    try:
                        api_key = request.json['custom_data']['API_KEY']
                        if api_key != "":
                            token_holder = User.find_by_api_token(api_key)
                            if token_holder is None:
                                return BaseController.errorGeneral("Unknown API_KEY holder"), 403
                    except KeyError:
                        return BaseController.errorGeneral("Missing API_KEY in custom_data"), 403

                    if auth_level == PostAuth.ADMINS_ONLY:
                        if token_holder.role != RoleType['ADMIN']:
                            return BaseController.errorGeneral("API_KEY does not belong to an administrator"), 403

                except KeyError as ex:
                    logging.error("Could not process custom_data")
                    return BaseController.errorGeneral("Could not process custom_data")

                # Redefine custom_data for the schema validators
                # request.json['custom_data'] = json_obj

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
