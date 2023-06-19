#!/usr/bin/env python
import argparse
import configparser
import multiprocessing
import os
import platform
import signal
import sys
from multiprocessing.connection import Listener

import redis as redis
from redis import Redis

from apps import WorkerType
from apps.alpr.enums import MultiProcessCommand

# Globals
worker_pids = {}
redis = redis.Redis()
parser = argparse.ArgumentParser("Redis/RQ-Python Worker Manager Server")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read("secrets.ini")

address = ('localhost', 3565)
listener = Listener(address, authkey=bytes(config['app']['secret_key'], 'utf-8'))
connection = listener.accept()


def start_worker(i, type):
    from rq import Connection, Worker
    import base64
    import logging
    import os
    import shutil
    import time
    from pathlib import Path

    import requests

    from apps.alpr.models.alpr_alert import ALPRAlert
    from apps.alpr.models.alpr_group import ALPRGroup
    from apps.alpr.enums import DataType
    from apps.alpr.models.custom_alert import CustomAlert
    from apps.alpr.models.settings import AgentSettings, EmailNotificationSettings, CameraSettings, GeneralSettings
    from apps.alpr.models.vehicle import Vehicle
    from apps.alpr.notify import Email, SMS, Tag
    from apps.alpr.routes.settings.cameras.manufacturers.Dahua import Dahua
    from apps.authentication.models import User, UserProfile
    from apps.authentication.routes import download_folder_name
    import apps.helpers as helper

    from apps import create_app
    from apps.config import config_dict

    # WARNING: Don't run with debug turned on in production!
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

    # The configuration
    get_config_mode = 'Debug' if DEBUG else 'Production'

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

    # Default queue name and worker name
    _name = "OpenALPR-Webhook Worker #{}".format(i)
    _queues = [WorkerType.General.value]

    if type == WorkerType.Camera:
        _name = "OpenALPR-Webhook Camera Worker #{}".format(i)
        _queues = [WorkerType.Camera.value]

    with Connection(connection=Redis()):
        worker = Worker(queues=_queues, name=_name)
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    if platform.system() == "Windows":
        sys.exit("Redis cannot fork on Windows! Only on *nix!")

    # Flush any stale jobs and workers
    redis.flushall()
    redis.flushdb()

    while True:
        message = connection.recv()
        if MultiProcessCommand.START_WORKER in message:
            # message = "start-worker CAMERA_ID"
            # message = ['start-worker', 'CAMERA_ID']
            worker_name = str(message).split(' ')[1]

            # Kill the worker if it's alive
            if worker_name in worker_pids.items():
                os.kill(worker_pids.worker_name, signal.SIGKILL)

            p = multiprocessing.Process(target=start_worker, args=(worker_name, WorkerType.Camera,))
            p.start()

            if platform.system() == "Linux":
                worker_pids.worker_name = p.pid
                print("PIDS: {}".format(worker_pids))

        if message == MultiProcessCommand.CLOSE_CONNECTION:
            connection.close()
            break

    listener.close()

    # Camera workers that force focus & zoom infinitely until told to stop or application stops.

    # General workers that download images and send alerts.
    for i in range(args.general_workers):
        p = multiprocessing.Process(target=start_worker, args=(i, WorkerType.General,))
        p.start()

        if platform.system() == "Linux":
            worker_pids.append(p.pid)


