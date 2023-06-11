from datetime import datetime

from flask_login import current_user

from apps import db, helpers
from sqlalchemy.ext.mutable import MutableDict
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
    def filter_epoch_start(self) -> "Vehicle":
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
            print(e)
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
