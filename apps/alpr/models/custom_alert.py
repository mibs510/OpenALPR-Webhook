import logging

from flask_login import current_user

from apps import db, helpers
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.mutable import MutableList, MutableDict

from apps.alpr import beautify
from apps.alpr.models.alpr_group import ALPRGroup
from apps.exceptions.exception import InvalidUsage
import apps.helpers as helper


class CustomAlert(db.Model):
    __bind_key__ = 'custom_alert'
    __tablename__ = 'custom_alert'

    id = db.Column(db.Integer, primary_key=True)
    alpr_group_id = db.Column(db.Integer)
    license_plate = db.Column(db.String)
    region_match = db.Column(db.Boolean)
    description = db.Column(db.String)
    notify_user_ids = db.Column(MutableList.as_mutable(db.JSON))
    submitted_by_user_id = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(CustomAlert, self).__init__(**kwargs)

    @classmethod
    def filter_by_id(cls, _id: int) -> "CustomAlert":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def filter_by_id_and_beautify(cls, _id: int) -> {}:
        custom_alert = cls.filter_by_id(_id)
        alpr_group = ALPRGroup()

        if custom_alert is not None:
            alpr_group = ALPRGroup.filter_by_id(custom_alert.alpr_group_id)

            if alpr_group is None:
                return None

        if custom_alert:
            dt = helpers.Timezone(current_user, msecs=True)
            return {
                'api_key': str(alpr_group.custom_data['API_KEY'][-4:]).upper(),
                'description': custom_alert.description,
                'region_match': custom_alert.region_match,
                'best_plate_number': custom_alert.license_plate,
                'uuid_jpg': alpr_group.uuid_jpg,
                'overview_jpeg': alpr_group.overview_jpeg,
                'vehicle_crop_jpeg': alpr_group.vehicle_crop_jpeg,
                'plate_crop_jpeg': alpr_group.best_plate['plate_crop_jpeg'],
                'agent_label': alpr_group.web_server_config['agent_label'],
                'agent_uid': alpr_group.agent_uid,
                'agent_version': alpr_group.agent_version,
                'agent_type': alpr_group.agent_type,
                'camera_label': alpr_group.web_server_config['camera_label'],
                'camera_id': alpr_group.camera_id,
                'gps_latitude': alpr_group.gps_latitude,
                'gps_longitude': alpr_group.gps_longitude,
                'country': beautify.name(alpr_group.country),
                'id': custom_alert.id,
                'alpr_group_id': custom_alert.alpr_group_id,
                'epoch_start': alpr_group.epoch_start,
                'epoch_start_datetime': dt.astimezone(alpr_group.epoch_start),
                'epoch_end': alpr_group.epoch_end,
                'epoch_end_datetime': dt.astimezone(alpr_group.epoch_start),
                'best_confidence_percent': alpr_group.best_confidence_percent,
                'best_region': beautify.country(alpr_group.best_region),
                'travel_direction_class_tag': beautify.direction(alpr_group.travel_direction),
                'travel_direction': round(float(alpr_group.travel_direction), 0),
                'vehicle_color_name': beautify.name(alpr_group.vehicle['color'][0]['name']),
                'vehicle_color_confidence': beautify.round_percentage(alpr_group.vehicle['color'][0]['confidence']),
                'vehicle_year_name': alpr_group.vehicle['year'][0]['name'],
                'vehicle_year_confidence': beautify.round_percentage(alpr_group.vehicle['year'][0]['confidence']),
                'vehicle_make_name': beautify.name(alpr_group.vehicle['make'][0]['name']),
                'vehicle_make_confidence': beautify.round_percentage(alpr_group.vehicle['make'][0]['confidence']),
                'vehicle_make_model_name': beautify.name(alpr_group.vehicle['make_model'][0]['name']),
                'vehicle_make_model_confidence': beautify.round_percentage(alpr_group.vehicle['make_model'][0]['confidence']),
                'vehicle_body_type_name': beautify.name(alpr_group.vehicle['body_type'][0]['name']),
                'vehicle_body_type_confidence': beautify.round_percentage(alpr_group.vehicle['body_type'][0]['confidence'])
            }

        else:
            return None

    @classmethod
    def filter_by_license_plate(cls, _license_plate: str) -> "CustomAlert":
        return cls.query.filter_by(license_plate=_license_plate).first()

    @classmethod
    def filter_by_submitted_user_id(cls, _submitted_by_user_id: int) -> ["CustomAlert"]:
        return cls.query.filter_by(submitted_by_user_id=_submitted_by_user_id).all()

    def get_dashboard_records(self, n=3) -> []:
        custom_alerts = \
            self.query.filter_by(submitted_by_user_id=current_user.id).order_by(CustomAlert.id.desc()).limit(n)
        data = []
        dt = helper.Timezone(current_user)

        for alert in custom_alerts:
            alpr_group = ALPRGroup.get_latest_by_best_plate_number(alert.license_plate)
            for record in alpr_group:
                data.append({
                    'id': record.id,
                    'month': dt.month(record.epoch_start),
                    'day': dt.day(record.epoch_start),
                    'plate_number': record.best_plate_number,
                    'epoch_time_datetime': dt.astimezone(record.epoch_start),
                    'site_name': record.web_server_config['agent_label'],
                    'camera_name': record.web_server_config['camera_label'],
                    'description': helper.shorten_description(alert.description)
                })
        return data

    def delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
