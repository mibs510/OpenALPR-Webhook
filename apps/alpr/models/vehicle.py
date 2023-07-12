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

from datetime import datetime

from flask_login import current_user

from apps import db, helpers
from sqlalchemy.ext.mutable import MutableDict

from apps.alpr import beautify
from apps.alpr.models.alpr_group import ALPRGroup
from apps.exceptions.exception import InvalidUsage


class Vehicle(db.Model):
    __bind_key__ = 'vehicle'
    __tablename__ = 'vehicle'

    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String, default="vehicle")
    version = db.Column(db.Integer)
    epoch_start = db.Column(db.Integer)
    epoch_end = db.Column(db.Integer)
    frame_start = db.Column(db.Integer)
    frame_end = db.Column(db.Integer)
    company_id = db.Column(db.String)
    agent_uid = db.Column(db.String)
    agent_version = db.Column(db.String)
    agent_type = db.Column(db.String)
    camera_id = db.Column(db.Integer)
    gps_latitude = db.Column(db.Integer)
    gps_longitude = db.Column(db.Integer)
    country = db.Column(db.String)
    vehicle_crop_jpeg = db.Column(db.String)
    overview_jpeg = db.Column(db.String)
    best_uuid = db.Column(db.String)
    best_uuid_epoch_ms = db.Column(db.Integer)
    best_image_width = db.Column(db.Integer)
    best_image_height = db.Column(db.Integer)
    travel_direction = db.Column(db.Integer)
    is_parked = db.Column(db.Boolean)
    is_preview = db.Column(db.Boolean)
    vehicle_signature = db.Column(db.String)
    vehicle = db.Column(MutableDict.as_mutable(db.JSON))
    custom_data = db.Column(MutableDict.as_mutable(db.JSON))

    # Custom
    travel_direction_class_tag = db.Column(db.String)
    vehicle_color_name = db.Column(db.String)
    vehicle_color_confidence = db.Column(db.String)
    vehicle_make_name = db.Column(db.String)
    vehicle_make_confidence = db.Column(db.String)
    vehicle_make_model_name = db.Column(db.String)
    vehicle_make_model_confidence = db.Column(db.String)
    vehicle_body_type_name = db.Column(db.String)
    vehicle_body_type_confidence = db.Column(db.String)
    vehicle_year_name = db.Column(db.String)
    vehicle_year_confidence = db.Column(db.String)
    vehicle_missing_plate_name = db.Column(db.String)
    vehicle_is_vehicle_name = db.Column(db.String)
    vehicle_is_vehicle_confidence = db.Column(db.String)
    uuid_jpg = db.Column(db.String)

    start_of_month_timestamp = datetime.now().timestamp()
    end_of_month_timestamp = datetime.now().timestamp()

    def __init__(self, **kwargs):
        super(Vehicle, self).__init__(**kwargs)
        self.start_of_month_timestamp = datetime.now().timestamp()
        self.end_of_month_timestamp = datetime.now().timestamp()
        self.collection = []

    @classmethod
    def filter_by_id(cls, _id: int) -> "Vehicle":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def filter_by_id_and_beautify(cls, _id: int) -> {}:
        record = cls.filter_by_id(_id)

        if record:
            dt = helpers.Timezone(current_user, msecs=True)
            return {
                'uuid_jpg': record.uuid_jpg,
                'overview_jpeg': record.overview_jpeg,
                'vehicle_crop_jpeg': record.vehicle_crop_jpeg,
                'agent_label': ALPRGroup.get_latest_agent_label(record.agent_uid),
                'agent_uid': record.agent_uid,
                'agent_version': record.agent_version,
                'agent_type': record.agent_type,
                'camera_label': ALPRGroup.get_latest_camera_label(record.camera_id),
                'camera_id': record.camera_id,
                'gps_latitude': record.gps_latitude,
                'gps_longitude': record.gps_longitude,
                'country': beautify.name(record.country),
                'id': record.id,
                'epoch_start': record.epoch_start,
                'epoch_start_datetime': dt.astimezone(record.epoch_start),
                'epoch_end': record.epoch_end,
                'epoch_end_datetime': dt.astimezone(record.epoch_end),
                'is_vehicle_confidence_percent': round(float(record.vehicle['is_vehicle'][0]['confidence']), 0),
                'travel_direction_class_tag': beautify.direction(record.travel_direction),
                'travel_direction': round(float(record.travel_direction), 0),
                'vehicle_color_name': record.vehicle_color_name,
                'vehicle_color_confidence': record.vehicle_color_confidence,
                'vehicle_year_name': record.vehicle_year_name,
                'vehicle_year_confidence': record.vehicle_year_confidence,
                'vehicle_make_name': record.vehicle_make_name,
                'vehicle_make_confidence': record.vehicle_make_confidence,
                'vehicle_make_model_name': record.vehicle_make_model_name,
                'vehicle_make_model_confidence': record.vehicle_make_model_confidence,
                'vehicle_body_type_name': record.vehicle_body_type_name,
                'vehicle_body_type_confidence': record.vehicle_body_type_confidence,
                'vehicle_signature': record.vehicle_signature
            }

        else:
            return None

    @classmethod
    def filter_epoch_start(self) -> ["Vehicle"]:
        self.collection = self.query.filter((Vehicle.epoch_start / 1000) >= self.start_of_month_timestamp).filter(
            (Vehicle.epoch_start / 1000) <= self.end_of_month_timestamp).all()
        return self.collection

    def get_records(self, n=8) -> []:
        records = self.query.order_by(Vehicle.id.desc()).limit(n)
        modified_records = []
        dt = helpers.Timezone(current_user)

        for record in records:
            record.epoch_start = dt.astimezone(record.epoch_start)
            record.epoch_end = dt.astimezone(record.epoch_end)
            modified_records.append(record)

        return modified_records

    @classmethod
    def query_all(cls) -> "Vehicle":
        return cls.query.all()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
