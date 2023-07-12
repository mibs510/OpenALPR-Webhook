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

from ...alpr.models.alpr_group import ALPRGroup
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import ModelSchema
from apps import db

# Defaults & missing
from ...authentication.models import User

default_missing_vehicle_path = [{"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                                {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0}]

default_missing_plate_indexes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

default_missing_candidates = [{"plate": "", "confidence": 0, "matches_template": 0}]

default_missing_best_plate = {"plate": "", "confidence": 0, "matches_template": 0, "plate_index": 0, "region": "",
                              "region_confidence": 0, "processing_time_ms": 0, "requested_topn": 0,
                              "coordinates": [{"x": 0, "y": 0}, {"x": 0, "y": 0}, {"x": 0, "y": 0}, {"x": 0, "y": 0}],
                              "plate_crop_jpeg": "", "vehicle_region": {"x": 0, "y": 0, "width": 0, "height": 0},
                              "vehicle_detected": 0,
                              "candidates": [{"plate": "", "confidence": 0, "matches_template": 0}]}

default_missing_plate_path = [{"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0},
                              {"x": 0, "y": 0, "w": 0, "h": 0, "t": 0, "f": 0}]

default_missing_vehicle = {
    "color": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}, {"name": "", "confidence": 0},
              {"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "make": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}, {"name": "", "confidence": 0},
             {"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "make_model": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}, {"name": "", "confidence": 0},
                   {"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "body_type": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}, {"name": "", "confidence": 0},
                  {"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "year": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}, {"name": "", "confidence": 0},
             {"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "orientation": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}, {"name": "", "confidence": 0},
                    {"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "missing_plate": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}],
    "is_vehicle": [{"name": "", "confidence": 0}, {"name": "", "confidence": 0}]}

default_missing_web_server_config = {"camera_label": "", "agent_label": ""}

default_missing_custom_data = {"API_KEY": ""}


class ALPRGroupSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        fields = (
            "id", "data_type", "version", "epoch_start", "epoch_end", "frame_start", "frame_end", "company_id",
            "agent_uid", "agent_version", "agent_type", "camera_id", "gps_latitude", "gps_longitude", "country",
            "uuids", "vehicle_path", "plate_indexes", "candidates", "best_plate", "best_confidence",
            "best_plate_number", "best_region", "best_region_confidence", "matches_template", "plate_path",
            "vehicle_crop_jpeg", "overview_jpeg", "best_uuid", "best_uuid_epoch_ms", "best_image_width",
            "best_image_height", "travel_direction", "is_parked", "is_preview", "vehicle_signature", "vehicle",
            "web_server_config", "direction_of_travel_id", "custom_data")
        model = ALPRGroup
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
    gps_latitude = fields.Float(default=None, missing=None)
    gps_longitude = fields.Float(default=None, missing=None)
    country = fields.String(default=None, missing=None)
    uuids = fields.List(fields.String(), default=None, missing=None)
    vehicle_path = fields.List(fields.Dict(), default=default_missing_vehicle_path,
                               missing=default_missing_vehicle_path)
    plate_indexes = fields.List(fields.Integer(), default=default_missing_plate_indexes,
                                missing=default_missing_plate_indexes)
    candidates = fields.List(fields.Dict(), default=default_missing_candidates, missing=default_missing_candidates)
    best_plate = fields.Dict(default=default_missing_best_plate, missing=default_missing_best_plate)
    best_confidence = fields.Float(default=None, missing=None)
    best_plate_number = fields.String(default=None, missing=None)
    best_region = fields.String(default=None, missing=None)
    best_region_confidence = fields.Float(default=None, missing=None)
    matches_template = fields.Boolean(default=None, missing=None)
    plate_path = fields.List(fields.Dict(), default=default_missing_plate_path, missing=default_missing_plate_path)
    vehicle_crop_jpeg = fields.String(default=None, missing=None)
    overview_jpeg = fields.String(default=None, missing=None),
    best_uuid = fields.String(default=None, missing=None)
    best_uuid_epoch_ms = fields.Integer(default=None, missing=None)
    best_image_width = fields.Integer(default=None, missing=None)
    best_image_height = fields.Integer(default=None, missing=None)
    travel_direction = fields.Float(default=None, missing=None)
    is_parked = fields.Boolean(default=None, missing=None)
    is_preview = fields.Boolean(default=None, missing=None)
    vehicle_signature = fields.String(default=None, missing=None)
    vehicle = fields.Dict(default=default_missing_vehicle, missing=default_missing_vehicle)
    web_server_config = fields.Dict(default=default_missing_web_server_config,
                                    missing=default_missing_web_server_config)
    direction_of_travel_id = fields.Integer(default=None, missing=None)
    custom_data = fields.Dict(default=default_missing_custom_data, missing=default_missing_custom_data)
