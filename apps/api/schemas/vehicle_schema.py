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

from ...alpr.models.vehicle import Vehicle
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import ModelSchema
from apps import db

# Defaults & missing
default_missing_custom_data = {"API_KEY": ""}


class VehicleSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        fields = ("id", "data_type", "version", "epoch_start", "epoch_end", "frame_start", "frame_end", "company_id",
                  "agent_uid", "agent_version", "agent_type", "camera_id", "gps_latitude", "gps_longitude", "country",
                  "vehicle_crop_jpeg", "overview_jpeg", "best_uuid", "best_uuid_epoch_ms", "best_image_width", 
                  "best_image_height", "travel_direction", "is_parked", "is_preview", "vehicle_signature", 
                  "vehicle", "time", "best_confidence_percent", "travel_direction_class_tag", "month", "day", 
                  "vehicle_color_name", "vehicle_color_confidence", "vehicle_make_name", "vehicle_make_confidence", 
                  "vehicle_make_model_name", "vehicle_make_model_confidence", "vehicle_body_type_name", 
                  "vehicle_body_type_confidence", "vehicle_year_name", "vehicle_year_confidence", 
                  "vehicle_missing_plate_name", "vehicle_is_vehicle_name", "vehicle_is_vehicle_confidence",
                  "custom_data")
        model = Vehicle
        unknown = EXCLUDE
        sqla_session = db.session
    data_type = fields.String(default=None, missing=None)
    version = fields.Integer(default=None, missing=None)
    epoch_start = fields.Integer(default=None, missing=None)
    epoch_end = fields.Integer(default=None, missing=None)
    frame_start = fields.Integer(default=None, missing=None)
    frame_end = fields.Integer(default=None, missing=None)
    company_id = fields.String(default=None, missing=None)
    agent_uid = fields.String(default=None, missing=None)
    agent_version = fields.String(default=None, missing=None)
    agent_type = fields.String(default=None, missing=None)
    camera_id = fields.Integer(default=None, missing=None)
    gps_latitude = fields.Integer(default=None, missing=None)
    gps_longitude = fields.Integer(default=None, missing=None)
    country = fields.String(default=None, missing=None)
    vehicle_crop_jpeg = fields.String(default=None, missing=None)
    overview_jpeg = fields.String(default=None, missing=None)
    best_uuid = fields.String(default=None, missing=None)
    best_uuid_epoch_ms = fields.Integer(default=None, missing=None)
    best_image_width = fields.Integer(default=None, missing=None)
    best_image_height = fields.Integer(default=None, missing=None)
    travel_direction = fields.Integer(default=None, missing=None)
    is_parked = fields.Boolean(default=None, missing=None)
    is_preview = fields.Boolean(default=None, missing=None)
    vehicle_signature = fields.String(default=None, missing=None)
    vehicle = fields.Dict(default={}, missing={})
    custom_data = fields.Dict(default=default_missing_custom_data, missing=default_missing_custom_data)
