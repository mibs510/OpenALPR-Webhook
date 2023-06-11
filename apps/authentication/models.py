import base64
import os
from pathlib import Path

from flask_login import UserMixin
from apps import db, login_manager
from apps.authentication.util import hash_pass
from sqlalchemy.exc import SQLAlchemyError
from apps.exceptions.exception import InvalidUsage
import datetime as dt
from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from apps.config import Config

RoleType = Config.USERS_ROLES
Status = Config.USERS_STATUS
VERIFIED_EMAIL = Config.VERIFIED_EMAIL

with open(Path(os.path.abspath(os.path.dirname(__file__ + "../../../../") +
                               "/apps/static/assets/img/user/avatar-2.jpg")).absolute(), "rb") as jpg_file:
    default_user_avatar = base64.b64encode(jpg_file.read()).decode("utf-8")


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.LargeBinary)
    avatar = db.Column(db.String, nullable=True, default=default_user_avatar)
    role = db.Column(db.Integer(), default=RoleType['USER'], nullable=False)
    status = db.Column(db.Integer(), default=Status['ACTIVE'], nullable=False)
    failed_logins = db.Column(db.Integer(), default=0)

    api_token = db.Column(db.String(100))
    api_token_ts = db.Column(db.String(100))

    verified_email = db.Column(db.Integer(), default=VERIFIED_EMAIL['not-verified'], nullable=False)

    oauth_twitter = db.Column(db.String(100), nullable=True)
    oauth_github = db.Column(db.String(100), nullable=True)

    date_created = db.Column(db.DateTime, default=dt.datetime.utcnow())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack its value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

    @classmethod
    def find_by_email(cls, _email: str) -> "User":
        return cls.query.filter_by(email=_email).first()

    @classmethod
    def find_by_username(cls, _username: str) -> "User":
        return cls.query.filter_by(username=_username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "User":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_api_token(cls, token: str) -> "User":
        return cls.query.filter_by(api_token=token).first()

    @classmethod
    def get_list_of_users_w_user_profiles(cls) -> []:
        users = cls.query.all()
        users_list = []
        for user in users:
            for profile in UserProfile.query.filter_by(user=user.id):
                if user.status == Status['ACTIVE']:
                    users_list.append({
                        'id': user.id,
                        'email': user.email,
                        'full_name': profile.full_name,
                        'username': user.username
                    })
        return users_list

    @classmethod
    def get_number_of_users(cls) -> int:
        return cls.query.count()

    def save(self) -> None:
        try:
            # Make the first user admin
            if self.get_number_of_users() == 0:
                self.role = RoleType['ADMIN']
            db.session.add(self)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=True, default='')
    bio = db.Column(db.String, nullable=True, default='')
    address = db.Column(db.String, nullable=True, default='')
    zipcode = db.Column(db.String, nullable=True, default='')
    phone = db.Column(db.String, nullable=True, default='')
    email = db.Column(db.String, unique=True, nullable=True)
    website = db.Column(db.String, nullable=True, default='')
    image = db.Column(db.String, nullable=True, default=default_user_avatar)
    timezone = db.Column(db.String, default="UTC")
    user = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user_id = relationship(User, uselist=False, backref="profile")
    date_created = db.Column(db.DateTime, default=dt.datetime.utcnow())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def find_by_id(cls, _id: int) -> "UserProfile":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user_id(cls, _id: int) -> "UserProfile":
        return cls.query.filter_by(user=_id).first()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(User)
