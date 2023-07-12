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
from apps.alpr.models.alpr_group import ALPRGroup
import apps.alpr.beautify as beautify
import time


class ALPRGroupService(Resource):
    def create(self, request_data: ALPRGroup):
        new_alpr_group = ALPRGroup()
        new_alpr_group.data_type = request_data.data_type
        new_alpr_group.version = request_data.version
        new_alpr_group.epoch_start = request_data.epoch_start
        new_alpr_group.epoch_end = request_data.epoch_end
        new_alpr_group.frame_start = request_data.frame_start
        new_alpr_group.frame_end = request_data.frame_end
        new_alpr_group.company_id = request_data.company_id
        new_alpr_group.agent_uid = request_data.agent_uid
        new_alpr_group.agent_version = request_data.agent_version
        new_alpr_group.agent_type = request_data.agent_type
        new_alpr_group.camera_id = request_data.camera_id
        new_alpr_group.gps_latitude = request_data.gps_latitude
        new_alpr_group.gps_longitude = request_data.gps_longitude
        new_alpr_group.country = request_data.country
        new_alpr_group.uuids = request_data.uuids
        new_alpr_group.vehicle_path = request_data.vehicle_path
        new_alpr_group.plate_indexes = request_data.plate_indexes
        new_alpr_group.candidates = request_data.candidates
        new_alpr_group.best_plate = request_data.best_plate
        new_alpr_group.best_confidence = request_data.best_confidence
        new_alpr_group.best_plate_number = request_data.best_plate_number
        new_alpr_group.best_region = request_data.best_region
        new_alpr_group.best_region_confidence = request_data.best_region_confidence
        new_alpr_group.matches_template = request_data.matches_template
        new_alpr_group.plate_path = request_data.plate_path
        new_alpr_group.vehicle_crop_jpeg = request_data.vehicle_crop_jpeg
        new_alpr_group.overview_jpeg = request_data.overview_jpeg
        new_alpr_group.best_uuid = request_data.best_uuid
        new_alpr_group.best_uuid_epoch_ms = request_data.best_uuid_epoch_ms
        new_alpr_group.best_image_width = request_data.best_image_width
        new_alpr_group.best_image_height = request_data.best_image_height
        new_alpr_group.travel_direction = request_data.travel_direction
        new_alpr_group.is_parked = request_data.is_parked
        new_alpr_group.is_preview = request_data.is_preview
        new_alpr_group.vehicle_signature = request_data.vehicle_signature
        new_alpr_group.vehicle = request_data.vehicle
        new_alpr_group.web_server_config = request_data.web_server_config
        new_alpr_group.direction_of_travel_id = request_data.direction_of_travel_id
        new_alpr_group.custom_data = request_data.custom_data

        # Custom
        new_alpr_group.best_confidence_percent = beautify.round_percentage(str(request_data.best_confidence))
        new_alpr_group.travel_direction_class_tag = beautify.direction(request_data.travel_direction)

        new_alpr_group.save()
        return new_alpr_group
