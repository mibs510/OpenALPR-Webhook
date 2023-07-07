import logging
import os
import platform
import subprocess
import time
from datetime import datetime

import setproctitle
from flask_ipban import IpBan
from flask_migrate import Migrate
from redis import Redis
from rq import Queue
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy, declarative_base
from importlib import import_module
from flask_mail import Mail

import log
import version
from apps.alpr.ipban_config import IPBanConfig
from worker_manager import WorkerManager
from worker_manager_enums import WorkerType, WMSCommand

setproctitle.setproctitle("OpenALPR-Webhook")
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
default_q = Queue(WorkerType.General.value, connection=Redis())
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
                        'alpr.routes.settings.users', 'alpr.routes.vehicle', 'home'):
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
    def initialize_cache():
        # Initiate cache when needed
        from apps.alpr.models.cache import Cache
        now = datetime.now()
        last_year = now.year - 1
        this_year = now.year
        next_year = now.year + 1

        Cache.filter_by_year(last_year)
        Cache.filter_by_year(this_year)
        Cache.filter_by_year(next_year)

    @app.before_first_request
    def initialize_settings():
        # Create default settings when needed
        from apps.alpr.models.settings import GeneralSettings
        settings = GeneralSettings.get_settings()

        if settings is None:
            settings = GeneralSettings()
            settings.save()

    @app.before_first_request
    def start_workers():
        start_redis_workers()


def start_redis_workers():
    # Start redis workers on Linux only
    if platform.system() == "Linuxx":
        # Worker Manager Server
        worker_manager_server = WorkerManager(WMSCommand.ACK)
        worker_manager_server.debug = True
        try:
            subprocess.Popen(['python3', os.path.abspath(os.path.dirname(__file__) + "/..") +
                              '/worker_manager_server.py'])
            time.sleep(3)
            worker_manager_server.send()
        except Exception as ex:
            logging.error(ex)

        if worker_manager_server.last_connection():
            # General workers to download UUID images from agents
            from apps.alpr.models.settings import AgentSettings
            enabled_agents = AgentSettings.get_all_enabled()
            for agent in enabled_agents:
                worker_manager_server.command = WMSCommand.START_WORKER
                worker_manager_server.worker_type = WorkerType.General
                worker_manager_server.worker_id = agent.agent_uid
                worker_manager_server.send()
            # Cameras
            from apps.alpr.models.settings import CameraSettings
            from apps.alpr import queue
            enabled_cameras = CameraSettings.get_all_enabled()
            try:
                for camera in enabled_cameras:
                    worker_manager_server.command = WMSCommand.START_WORKER
                    worker_manager_server.worker_type = WorkerType.Camera
                    worker_manager_server.worker_id = camera.camera_id
                    worker_manager_server.send()
                    time.sleep(1)
                    # Add the function to the queue
                    q = Queue(camera.camera_id, connection=Redis())
                    q.enqueue(queue.focus_camera, args=(camera.camera_id,), job_timeout=-1)
            except Exception as ex:
                logging.exception(ex)
        else:
            logging.error("Last connection to Worker Manager Server failed. Could not spin up redis workers!")


def create_app(config) -> Flask:
    log.init("OpenALPR-Webhook.log")
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
