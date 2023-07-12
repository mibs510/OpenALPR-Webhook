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

import datetime
from flask_restx import Resource
from apps.alpr.models.alpr_alert import ALPRAlert
import apps.alpr.beautify as beautify
from apps.messages import Messages

message = Messages.message


class ALPRAlertService(Resource):
    def create(self, request_data: ALPRAlert):
        new_alpr_alert = ALPRAlert()
        new_alpr_alert.data_type = request_data.data_type
        new_alpr_alert.version = request_data.version
        new_alpr_alert.epoch_time = request_data.epoch_time
        new_alpr_alert.agent_uid = request_data.agent_uid
        new_alpr_alert.alert_list = request_data.alert_list
        new_alpr_alert.alert_list_id = request_data.alert_list_id
        new_alpr_alert.site_name = request_data.site_name
        new_alpr_alert.camera_name = request_data.camera_name
        new_alpr_alert.camera_number = request_data.camera_number
        new_alpr_alert.plate_number = request_data.plate_number
        new_alpr_alert.description = request_data.description
        new_alpr_alert.list_type = request_data.list_type
        new_alpr_alert.group = request_data.group
        new_alpr_alert.custom_data = request_data.custom_data

        # Custom
        new_alpr_alert.best_confidence_percent = beautify.round_percentage(request_data.group['best_confidence'])
        new_alpr_alert.travel_direction_class_tag = beautify.direction(request_data.group['travel_direction'])

        new_alpr_alert.save()
        return new_alpr_alert
