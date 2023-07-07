import logging
from datetime import datetime

from flask_login import current_user

from apps import db, helpers
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.mutable import MutableDict, MutableList

from apps.alpr import beautify
from apps.exceptions.exception import InvalidUsage


class ALPRGroup(db.Model):
    __bind_key__ = 'alpr_group'
    __tablename__ = 'alpr_group'

    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String, default="alpr_group")
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
    uuids = db.Column(MutableList.as_mutable(db.JSON))
    vehicle_path = db.Column(MutableList.as_mutable(db.JSON))
    plate_indexes = db.Column(MutableList.as_mutable(db.JSON))
    candidates = db.Column(MutableList.as_mutable(db.JSON))
    best_plate = db.Column(MutableDict.as_mutable(db.JSON))
    best_confidence = db.Column(db.Integer)
    best_plate_number = db.Column(db.String)
    best_region = db.Column(db.String)
    best_region_confidence = db.Column(db.Integer)
    matches_template = db.Column(db.String)  # Boolean
    plate_path = db.Column(MutableList.as_mutable(db.JSON))
    vehicle_crop_jpeg = db.Column(db.String)
    overview_jpeg = db.Column(db.String)
    best_uuid = db.Column(db.String)
    best_uuid_epoch_ms = db.Column(db.Integer)
    best_image_width = db.Column(db.Integer)
    best_image_height = db.Column(db.Integer)
    travel_direction = db.Column(db.Integer)
    is_parked = db.Column(db.String)  # Boolean
    is_preview = db.Column(db.String)  # Boolean
    vehicle_signature = db.Column(db.String)
    vehicle = db.Column(MutableDict.as_mutable(db.JSON))
    web_server_config = db.Column(MutableDict.as_mutable(db.JSON))
    direction_of_travel_id = db.Column(db.String)
    custom_data = db.Column(MutableDict.as_mutable(db.JSON))

    # Custom
    best_confidence_percent = db.Column(db.String)
    travel_direction_class_tag = db.Column(db.String)
    uuid_jpg = db.Column(db.String)

    def __init__(self, **kwargs):
        super(ALPRGroup, self).__init__(**kwargs)
        self.start_of_month_timestamp = datetime.now().timestamp()
        self.end_of_month_timestamp = datetime.now().timestamp()
        self.collection = []

    @classmethod
    def filter_by_id(cls, _id: int) -> "ALPRGroup":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def filter_by_best_plate_number(cls, best_plate_number: str) -> "[ALPRGroup]":
        return cls.query.filter_by(best_plate_number=best_plate_number).order_by(ALPRGroup.id.desc()).all()

    @classmethod
    def filter_by_id_and_beautify(cls, _id: int) -> {}:
        record = cls.filter_by_id(_id)

        if record:
            dt = helpers.Timezone(current_user, msecs=True)
            return {
                'best_plate_number': record.best_plate_number,
                'uuid_jpg': record.uuid_jpg,
                'overview_jpeg': record.overview_jpeg,
                'vehicle_crop_jpeg': record.vehicle_crop_jpeg,
                'plate_crop_jpeg': record.best_plate['plate_crop_jpeg'],
                'agent_label': record.web_server_config['agent_label'],
                'agent_uid': record.agent_uid,
                'agent_version': record.agent_version,
                'agent_type': record.agent_type,
                'camera_label': record.web_server_config['camera_label'],
                'camera_id': record.camera_id,
                'gps_latitude': record.gps_latitude,
                'gps_longitude': record.gps_longitude,
                'country': beautify.name(record.country),
                'id': record.id,
                'epoch_start': record.epoch_start,
                'epoch_start_datetime': dt.astimezone(record.epoch_start),
                'epoch_end': record.epoch_end,
                'epoch_end_datetime': dt.astimezone(record.epoch_end),
                'best_confidence_percent': record.best_confidence_percent,
                'best_region': beautify.country(record.best_region),
                'travel_direction_class_tag': beautify.direction(record.travel_direction),
                'travel_direction': round(float(record.travel_direction), 0),
                'vehicle_color_name': beautify.name(record.vehicle['color'][0]['name']),
                'vehicle_color_confidence': beautify.round_percentage(record.vehicle['color'][0]['confidence']),
                'vehicle_year_name': record.vehicle['year'][0]['name'],
                'vehicle_year_confidence': beautify.round_percentage(record.vehicle['year'][0]['confidence']),
                'vehicle_make_name': beautify.name(record.vehicle['make'][0]['name']),
                'vehicle_make_confidence': beautify.round_percentage(record.vehicle['make'][0]['confidence']),
                'vehicle_make_model_name': beautify.name(record.vehicle['make_model'][0]['name']),
                'vehicle_make_model_confidence': beautify.round_percentage(record.vehicle['make_model'][0]['confidence']),
                'vehicle_body_type_name': beautify.name(record.vehicle['body_type'][0]['name']),
                'vehicle_body_type_confidence': beautify.round_percentage(record.vehicle['body_type'][0]['confidence'])
            }

        else:
            return None

    @classmethod
    def get_latest_agent_label(cls, _agent_uid: str) -> str:
        record = cls.query.filter_by(agent_uid=_agent_uid).order_by(ALPRGroup.id.desc()).first()
        return record.web_server_config['agent_label']

    @classmethod
    def get_latest_agent_type(cls, _agent_uid: str) -> str:
        record = cls.query.filter_by(agent_uid=_agent_uid).order_by(ALPRGroup.id.desc()).first()
        return record.agent_type

    @classmethod
    def get_latest_agent_version(cls, _agent_uid: str) -> str:
        record = cls.query.filter_by(agent_uid=_agent_uid).order_by(ALPRGroup.id.desc()).first()
        return record.agent_version

    @classmethod
    def get_latest_camera_label(cls, _camera_id: int) -> str:
        record = cls.query.filter_by(camera_id=_camera_id).order_by(ALPRGroup.id.desc()).first()
        return record.web_server_config['camera_label']

    @classmethod
    def get_latest_camera_gps_latitude(cls, _camera_id: int) -> str:
        record = cls.query.filter_by(camera_id=_camera_id).order_by(ALPRGroup.id.desc()).first()
        return record.gps_latitude

    @classmethod
    def get_latest_camera_country(cls, _camera_id: int) -> str:
        record = cls.query.filter_by(camera_id=_camera_id).order_by(ALPRGroup.id.desc()).first()
        return record.country

    @classmethod
    def get_latest_camera_gps_longitude(cls, _camera_id: int) -> str:
        record = cls.query.filter_by(camera_id=_camera_id).order_by(ALPRGroup.id.desc()).first()
        return record.gps_longitude

    @classmethod
    def get_latest_by_best_plate_number(cls, best_plate_number: str, limit=2) -> "[ALPRGroup]":
        return cls.query.filter_by(best_plate_number=best_plate_number).order_by(ALPRGroup.id.desc()).limit(limit)

    @classmethod
    def get_oldest_agent_epoch_start(cls, _agent_uid: int) -> int:
        record = cls.query.filter_by(agent_uid=_agent_uid).order_by(ALPRGroup.id.asc()).first()
        return record.epoch_start

    @classmethod
    def get_oldest_camera_epoch_start(cls, _camera_id: int) -> int:
        record = cls.query.filter_by(camera_id=_camera_id).order_by(ALPRGroup.id.asc()).first()
        return record.epoch_start

    def filter_epoch_start(self) -> []:
        self.collection = self.query.filter((ALPRGroup.epoch_start / 1000) >= self.start_of_month_timestamp).filter(
            (ALPRGroup.epoch_start / 1000) <= self.end_of_month_timestamp).all()
        return self.collection

    def get_all_agent_uids(self) -> {}:
        if self.collection is None:
            return {}

        agent_uids = {}

        # Add every unique agent_uid for that month onto a list
        for record in self.collection:
            if record.agent_uid not in agent_uids:
                agent_uids[record.agent_uid] = record.web_server_config['agent_label']

        return agent_uids

    def get_cameras_and_counts(self) -> {}:
        if self.collection is None:
            return {}

        cameras = []

        # Add every camera for that month onto a list
        for record in self.collection:
            cameras.append(record.camera_id)

        # Go through each camera and get a count
        dictionary = {}
        for camera in cameras:
            dictionary[camera] = cameras.count(camera)

        # Sort the dictionary from greatest to least
        return dict(sorted(dictionary.items(), key=lambda count: count[1], reverse=True))

    def get_all_regions(self) -> {}:
        if self.collection is None:
            return {}

        regions = []

        # Add every region for that month onto a list
        for record in self.collection:
            regions.append(record.best_region)

        # Go through each region and get a count
        dictionary = {}
        for region in regions:
            dictionary[region] = regions.count(region)

        # Sort the dictionary from greatest to least
        return dict(sorted(dictionary.items(), key=lambda count: count[1], reverse=True))

    def get_dashboard_records(self, n=8) -> []:
        records = self.query.order_by(ALPRGroup.id.desc()).limit(n)
        modified_records = []
        dt = helpers.Timezone(current_user)

        for record in records:
            modified_records.append({
                'agent_label': record.web_server_config['agent_label'],
                'camera_label': record.web_server_config['camera_label'],
                'id': record.id,
                'best_plate_number': record.best_plate_number,
                'travel_direction_class_tag': record.travel_direction_class_tag,
                'best_confidence_percent': record.best_confidence_percent,
                'epoch_start_datetime': dt.astimezone(record.epoch_start)
            })

        return modified_records

    def query_all(self) -> []:
        return self.query.all()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            logging.exception(e)
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def to_dic(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
