#!/usr/bin/env python
import argparse
import multiprocessing
import platform
import sys

import redis as redis
from redis import Redis

from apps import WorkerType

# Globals
worker_pids = []
redis = redis.Redis()
parser = argparse.ArgumentParser("Start camera and general workers")
parser.add_argument('--camera_workers', '-c', type=int, help="Number of workers for camera focus & zoom")
parser.add_argument('--general_workers', '-g', type=int, help="Number of general workers")
args = parser.parse_args()


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
    if args.camera_workers is None or args.camera_workers <= 0:
        sys.exit("Camera workers must be > 0")

    if args.camera_workers is None or args.camera_workers <= 0:
        sys.exit("Camera workers must be > 0")

    if platform.system() == "Windows":
        sys.exit("Redis cannot fork on Windows! Only on *nix!")

    # Flush any stale jobs and workers
    redis.flushall()
    redis.flushdb()

    # Camera workers that force focus & zoom infinitely until told to stop or application stops.
    for i in range(args.camera_workers):
        p = multiprocessing.Process(target=start_worker, args=(i, WorkerType.Camera,))
        p.start()

        if platform.system() == "Linux":
            worker_pids.append(p.pid)

    # General workers that download images and send alerts.
    for i in range(args.general_workers):
        p = multiprocessing.Process(target=start_worker, args=(i, WorkerType.General,))
        p.start()

        if platform.system() == "Linux":
            worker_pids.append(p.pid)

    print("PIDS: {}".format(worker_pids))
