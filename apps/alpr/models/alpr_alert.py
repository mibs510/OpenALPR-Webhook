from datetime import datetime

from flask_login import current_user

from apps import db, helpers
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.mutable import MutableDict

from apps.alpr import beautify
from apps.exceptions.exception import InvalidUsage


class ALPRAlert(db.Model):
    __bind_key__ = 'alpr_alert'
    __tablename__ = 'alpr_alert'

    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String, default="alpr_alert")
    version = db.Column(db.Integer)
    epoch_time = db.Column(db.Integer)
    agent_uid = db.Column(db.String)
    alert_list = db.Column(db.String)
    alert_list_id = db.Column(db.Integer)
    site_name = db.Column(db.String)
    camera_name = db.Column(db.String)
    camera_number = db.Column(db.Integer)
    plate_number = db.Column(db.String)
    description = db.Column(db.String)
    list_type = db.Column(db.String)
    group = db.Column(MutableDict.as_mutable(db.JSON))
    custom_data = db.Column(MutableDict.as_mutable(db.JSON))

    # Custom
    best_confidence_percent = db.Column(db.String)
    travel_direction_class_tag = db.Column(db.String)
    uuid_jpg = db.Column(db.String)

    start_of_month_timestamp = datetime.now().timestamp()
    end_of_month_timestamp = datetime.now().timestamp()

    def __init__(self, **kwargs):
        super(ALPRAlert, self).__init__(**kwargs)
        self.start_of_month_timestamp = datetime.now().timestamp()
        self.end_of_month_timestamp = datetime.now().timestamp()
        self.collection = []

    @classmethod
    def filter_by_id(cls, _id: int) -> "ALPRAlert":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def filter_by_id_and_beautify(cls, _id: int) -> {}:
        record = cls.filter_by_id(_id)

        if record:
            dt = helpers.Timezone(current_user, msecs=True)
            return {
                'api_key': str(record.custom_data['API_KEY'][-4:]).upper(),
                'description': record.description,
                'alert_list_id': record.alert_list_id,
                'list_type': record.list_type,
                'best_plate_number': record.plate_number,
                'uuid_jpg': record.uuid_jpg,
                'overview_jpeg': record.group['overview_jpeg'],
                'vehicle_crop_jpeg': record.group['vehicle_crop_jpeg'],
                'plate_crop_jpeg': record.group['best_plate']['plate_crop_jpeg'],
                'agent_label': record.site_name,
                'agent_uid': record.agent_uid,
                'agent_version': record.group['agent_version'],
                'agent_type': record.group['agent_type'],
                'camera_label': record.camera_name,
                'camera_id': record.camera_number,
                'gps_latitude': record.group['gps_latitude'],
                'gps_longitude': record.group['gps_longitude'],
                'country': beautify.name(record.group['country']),
                'id': record.id,
                'epoch_time': record.epoch_time,
                'epoch_datetime': dt.astimezone(record.epoch_time),
                'best_confidence_percent': record.best_confidence_percent,
                'best_region': beautify.country(record.group['best_region']),
                'travel_direction_class_tag': record.travel_direction_class_tag,
                'travel_direction': round(float(record.group['travel_direction']), 0),
                'vehicle_color_name': beautify.name(record.group['vehicle']['color'][0]['name']),
                'vehicle_color_confidence': beautify.round_percentage(
                    record.group['vehicle']['color'][0]['confidence']),
                'vehicle_year_name': record.group['vehicle']['year'][0]['name'],
                'vehicle_year_confidence': beautify.round_percentage(record.group['vehicle']['year'][0]['confidence']),
                'vehicle_make_name': beautify.name(record.group['vehicle']['make'][0]['name']),
                'vehicle_make_confidence': beautify.round_percentage(record.group['vehicle']['make'][0]['confidence']),
                'vehicle_make_model_name': beautify.name(record.group['vehicle']['make_model'][0]['name']),
                'vehicle_make_model_confidence': beautify.round_percentage(
                    record.group['vehicle']['make_model'][0]['confidence']),
                'vehicle_body_type_name': beautify.name(record.group['vehicle']['body_type'][0]['name']),
                'vehicle_body_type_confidence': beautify.round_percentage(
                    record.group['vehicle']['body_type'][0]['confidence'])
            }

        else:
            return None

    def filter_epoch_time(self) -> "ALPRAlert":
        self.collection = self.query.filter((ALPRAlert.epoch_time / 1000) >= self.start_of_month_timestamp).filter(
            (ALPRAlert.epoch_time / 1000) <= self.end_of_month_timestamp).all()
        return self.collection

    def get_dashboard_records(self, n=3) -> []:
        records = self.query.order_by(ALPRAlert.id.desc()).limit(n)
        modified_records = []
        dt = helpers.Timezone(current_user)

        for record in records:
            modified_records.append({
                'id': record.id,
                'month': dt.month(record.epoch_time),
                'day': dt.day(record.epoch_time),
                'plate_number': record.plate_number,
                'list_type': record.list_type,
                'epoch_time_datetime': dt.astimezone(record.epoch_time),
                'site_name': record.site_name,
                'camera_name': record.camera_name
            })

        return modified_records

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
