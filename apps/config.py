import configparser
import os
from os.path import exists
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    RQ_DASHBOARD_REDIS_URL = "redis://127.0.0.1:6379"
    UPLOAD_FOLDER = 'apps/uploads/'
    DOWNLOAD_FOLDER = 'apps/downloads/'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    USERS_ROLES = {'ADMIN': 1, 'USER': 2}
    USERS_STATUS = {'ACTIVE': 1, 'SUSPENDED': 2}

    # check verified_email
    VERIFIED_EMAIL = {'verified': 1, 'not-verified': 2}

    LOGIN_ATTEMPT_LIMIT = 7

    DEFAULT_IMAGE_URL = 'static/assets/images/'

    # Set up secrets
    if not exists("secrets.ini"):
        config = configparser.ConfigParser()
        config['app'] = {'secret_key': secrets.token_hex(),
                         'secret_password_salt': secrets.SystemRandom().getrandbits(128)}
        with open("secrets.ini", 'w', encoding='utf-8') as configini:
            config.write(configini)

    config = configparser.ConfigParser()
    config.read("secrets.ini")

    SECRET_KEY = os.getenv('SECRET_KEY', config['app']['secret_key'])
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', config['app']['secret_password_salt'])

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/app.sqlite')
    SQLALCHEMY_BINDS = {
        'alpr_alert': 'sqlite:///' + os.path.join(basedir, 'db/alpr_alert.sqlite'),
        'alpr_group': 'sqlite:///' + os.path.join(basedir, 'db/alpr_group.sqlite'),
        'cache': 'sqlite:///' + os.path.join(basedir, 'db/cache.sqlite'),
        'custom_alert': 'sqlite:///' + os.path.join(basedir, 'db/custom_alert.sqlite'),
        'settings': 'sqlite:///' + os.path.join(basedir, 'db/settings.sqlite'),
        'vehicle': 'sqlite:///' + os.path.join(basedir, 'db/vehicle.sqlite'),
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
