import platform
import subprocess
from datetime import datetime

from flask_ipban import IpBan
from flask_migrate import Migrate
from redis import Redis
from rq import Queue
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy, declarative_base
from importlib import import_module
from flask_mail import Mail

import version
from apps.alpr.ipban_config import IPBanConfig
from apps.alpr.enums import WorkerType

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
default_q = Queue(WorkerType.General.value, connection=Redis())
camera_q = Queue(WorkerType.Camera.value, connection=Redis())
Base = declarative_base()
login_manager = LoginManager()
ip_ban_config = IPBanConfig()
ip_ban = IpBan(ban_count=ip_ban_config.ban_count, ban_seconds=ip_ban_config.ban_seconds, persist=ip_ban_config.persist,
               record_dir=ip_ban_config.record_dir, ip_header=ip_ban_config.ip_header)


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('api', 'authentication', 'alpr.routes.alert', 'alpr.routes.alerts',
                        'alpr.routes.alerts.custom', 'alpr.routes.alerts.rekor', 'alpr.routes.capture',
                        'alpr.routes.search', 'alpr.routes.settings', 'alpr.routes.settings.agents',
                        'alpr.routes.settings.cameras', 'alpr.routes.settings.general',
                        'alpr.routes.settings.maintenance', 'alpr.routes.settings.maintenance.rq_dashboard',
                        'alpr.routes.settings.notifications', 'alpr.routes.settings.profile',
                        'alpr.routes.settings.users', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.context_processor
    def inject_global_vars():
        return dict(app_version=version.__version__)

    @app.before_first_request
    def initialize_databases():
        # db.create_all()
        pass

    @app.before_first_request
    def initialize_settings():
        # Initiate cache when needed
        from apps.alpr.models.cache import Cache
        now = datetime.now()
        last_year = now.year - 1
        this_year = now.year
        next_year = now.year + 1

        Cache.filter_by_year(last_year)
        Cache.filter_by_year(this_year)
        Cache.filter_by_year(next_year)

        # Create default settings when needed
        from apps.alpr.models.settings import GeneralSettings
        settings = GeneralSettings.get_settings()

        if settings is None:
            settings = GeneralSettings()
            settings.save()

        # Start redis workers on Linux only
        if platform.system() == "Linux":
            from apps.alpr.models.settings import CameraSettings
            camera_workers = len(CameraSettings.get_all_enabled())
            workers_cmd = subprocess.run(["./workers.py", "-c", camera_workers, "-g", camera_workers])
            print("workers_cmd.returncode = {}".format(workers_cmd.returncode))
            print("workers_cmd.stdout = {}".format(workers_cmd.stdout))
            print("workers_cmd.stderr = {}".format(workers_cmd.stderr))


def create_app(config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    mail.init_app(app)
    ip_ban.init_app(app)
    register_extensions(app)
    register_blueprints(app)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    configure_database(app)

    with app.app_context():
        db.create_all()
        return app
