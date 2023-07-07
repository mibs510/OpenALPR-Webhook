import base64
import enum
import os
from datetime import datetime
from pathlib import Path

from redis import Redis
from rq import Queue, Worker

from apps import db

from sqlalchemy.exc import SQLAlchemyError
from apps.exceptions.exception import InvalidUsage


with open(Path(os.path.abspath(os.path.dirname(__file__ + "../../../../") +
                               "/static/assets/img/brand/fishing-hook-bl.svg")).absolute(), "rb") as svg_file:
    default_org_logo = base64.b64encode(svg_file.read()).decode("utf-8")


class PostAuth(enum.Enum):
    DISABLE_POSTING = 0
    NO_AUTH = 1
    USERS_ADMINS = 2
    ADMINS_ONLY = 3


class AgentSettings(db.Model):
    __bind_key__ = 'settings'
    __tablename__ = 'AgentSettings'

    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    agent_uid = db.Column(db.String)
    agent_label = db.Column(db.String)
    ip_hostname = db.Column(db.String)
    port = db.Column(db.Integer, default=8355)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())

    def __init__(self, agent_uid: int, agent_label: str):
        self.agent_uid = agent_uid
        self.agent_label = agent_label

    @classmethod
    def filter_by_agent_uid(cls, agent_uid: str) -> "AgentSettings":
        return cls.query.filter_by(agent_uid=agent_uid).first()

    @classmethod
    def filter_by_id(cls, id: str) -> "AgentSettings":
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all(cls, _agent_uid: str) -> ["AgentSettings"]:
        return cls.query.all()

    @classmethod
    def get_all_enabled(cls) -> ["AgentSettings"]:
        return cls.query.filter_by(enabled=True)

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)


class CameraSettings(db.Model):
    __bind_key__ = 'settings'
    __tablename__ = 'CameraSettings'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer)
    camera_label = db.Column(db.String)
    hostname = db.Column(db.String)
    port = db.Column(db.Integer)
    username = db.Column(db.String)
    password = db.Column(db.String)
    focus = db.Column(db.String)
    zoom = db.Column(db.String)
    focus_zoom_interval_check = db.Column(db.Integer)
    notify_on_failed_interval_check = db.Column(db.Boolean)
    manufacturer = db.Column(db.String)
    enable = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())

    def __init__(self, camera_id: int, camera_label: str):
        self.camera_id = camera_id
        self.camera_label = camera_label

    @classmethod
    def filter_by_camera_id(cls, _camera_id: int) -> "CameraSettings":
        return cls.query.filter_by(camera_id=_camera_id).first()

    @classmethod
    def filter_by_id(cls, _id: int) -> "CameraSettings":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all_enabled(cls) -> ["CameraSettings"]:
        return cls.query.filter_by(enable=True)

    @classmethod
    def get_camera_label(cls, _camera_id: int) -> "CameraSettings":
        camera = cls.query.filter_by(camera_id=_camera_id).first()
        return camera.camera_label

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    @classmethod
    def start_wqs(cls):
        all_enabled_cameras = cls.query.filter_by(enabled=True)

        for camera in all_enabled_cameras:
            q = Queue(connection=Redis(), name=camera.id)
            Worker(name=camera.id, queues=q)


class EmailNotificationSettings(db.Model):
    __bind_key__ = 'settings'
    __tablename__ = 'EmailNotificationSettings'

    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    hostname = db.Column(db.String)
    port = db.Column(db.Integer)
    username_email = db.Column(db.String)
    password = db.Column(db.String)
    recipients = db.Column(db.String)

    @classmethod
    def get_recipients(cls) -> [str]:
        settings = cls.query.filter_by(id=id).first()
        recipients = settings.recipients

        return recipients.split(',')

    @classmethod
    def get_settings(cls) -> "EmailNotificationSettings":
        return cls.query.filter_by(id=1).first()

    @classmethod
    def is_enabled(cls) -> bool:
        settings = cls.query.filter_by(id=id).first()
        return settings.enabled

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)


class GeneralSettings(db.Model):
    __bind_key__ = 'settings'
    __tablename__ = 'GeneralSettings'

    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.String, default=default_org_logo)
    org_name = db.Column(db.String, default="OpenALPR-Webhook")
    post_auth = db.Column(db.Enum(PostAuth), default=PostAuth.ADMINS_ONLY)
    public_url = db.Column(db.String, default="https://openalpr-webhook")

    @classmethod
    def get_settings(cls) -> "GeneralSettings":
        return cls.query.filter_by(id=1).first()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)


class TwilioNotificationSettings(db.Model):
    __bind_key__ = 'settings'
    __tablename__ = 'TwilioNotificationSettings'

    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    account_sid = db.Column(db.String)
    auth_token = db.Column(db.String)
    phone_number = db.Column(db.String)
    recipients = db.Column(db.String)

    @classmethod
    def get_recipients(cls) -> []:
        settings = cls.query.filter_by(id=1).first()
        recipients = settings.recipients

        return recipients.split(',')

    @classmethod
    def get_settings(cls) -> "TwilioNotificationSettings":
        return cls.query.filter_by(id=1).first()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
