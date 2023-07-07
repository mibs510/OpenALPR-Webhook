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


def download_plate_image(agent_uid: str, img_uuid: str, data_type: str, foreign_id: int):
    # Make the application context available here. This function is forked into a separate process and the database
    # connections needs to be reintroduced.
    app = create_app(app_config)
    app.app_context().push()

    # Get agent IP/hostname & port
    agent = AgentSettings.filter_by_agent_uid(agent_uid)

    download_dir = os.path.abspath(os.path.dirname(__file__) + "../../../") + "/" + download_folder_name

    # Create directory when needed
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Email object
    email = Email()
    email.tag = Tag.AGENT.value
    email.subject = "Plate Image Save Failed"
    email.recipients = EmailNotificationSettings.recipients

    if agent is None:
        logging.info("Agent (ID: {}) does not exist.".format(agent_uid))
        raise Exception("Failed to download a plate image. Agent (ID: {}) does not exist.".format(agent_uid))
    elif agent.enabled:
        url = "http://{}:{}/img/{}.jpg".format(agent.ip_hostname, agent.port, img_uuid)
        try:
            logging.info("Downloading: {}".format(url))
            # Download it
            req = requests.get(url, stream=True)

            if req.status_code == 200:
                # Create a path to save it to
                full_file_path = Path(download_dir + img_uuid + ".jpg").absolute()
                # Write to disk
                with open(full_file_path, 'wb') as jpg:
                    shutil.copyfileobj(req.raw, jpg)
                logging.info("File downloaded, location: {}".format(full_file_path))
            else:
                logging.info("Failed to download high resolution plate image. HTTP status_code={}".format(
                    req.status_code))

                email.body = "⚠️ Failed to download high resolution image. " \
                             "HTTP status code from agent was not 200.\n\nLabel: {}\nUID: {}\n" \
                             "IMG UID: {}\nURL: {}\nHTTP Status: {}".format(
                    agent.agent_label, agent_uid, img_uuid, url, req.status_code)
                email.send()

                raise Exception("Failed to download high resolution plate image. HTTP status_code={}".format(
                    req.status_code))

        except Exception as ex:
            logging.info("Failed to download the plate image")

            email.body = "⚠️ Failed to download high resolution image. Incorrect IP/hostname & port? Make sure" \
                         "OpenALPR-Webhook can access the agent.\n\nLabel: {}\nUID: {}\nIMG UID: {}\n" \
                         "URL: {}\nException: {}".format(agent.agent_label, agent_uid, img_uuid, url, ex)
            email.send()
            raise Exception(ex)

        # Find the original record
        record = None
        dt = DataType(data_type)

        if dt == DataType.GROUP:
            record = ALPRGroup.filter_by_id(foreign_id)
        elif dt == DataType.ALERT:
            record = ALPRAlert.filter_by_id(foreign_id)
        elif dt == DataType.VEHICLE:
            record = Vehicle.filter_by_id(foreign_id)
        elif dt is None:
            raise Exception("Unknown data_type = {}".format(data_type))

        if record is not None:
            # Insert the image in the db
            try:
                # Read it while encoding it into base64
                with open(full_file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                uuid_jpg = encoded_string.decode("utf-8")

                # Insert into `uuid_jpg column`
                record.uuid_jpg = uuid_jpg

                # Save/update the db
                record.save()

                # Delete the .jpg afterwards
                if os.path.isfile(full_file_path):
                    os.remove(full_file_path)
                return True
            except Exception as ex:
                logging.exception(ex)
                logging.info("Failed to save the plate image")

                email.body = "⚠️ Failed to download high resolution image from agent.\n\n" \
                             "Label: {}\nUID: {}\nImage UID: {}\nException: {}\n".format(agent.agent_label,
                                                                                         agent.agent_uid, img_uuid, ex)
                email.send()

                # Delete the jpg if something happens above
                if os.path.isfile(full_file_path):
                    os.remove(full_file_path)
                raise Exception(ex)
        else:
            logging.error("Record #{} of type {} not found. dt = {}".format(foreign_id, data_type, dt))

    elif not agent.enabled:
        logging.info("Agent (Label: {}) is disabled.".format(agent.agent_label))


def focus_camera(camera_id: int):
    # Make the application context available here. This function is forked into a separate process and the database
    # connections needs to be reintroduced.
    app = create_app(app_config)
    app.app_context().push()

    # Email
    email = Email()
    email.tag = Tag.CAMERA.value
    email.subject = "Force Focus & Zoom Failed"
    email.recipients = EmailNotificationSettings.recipients

    # Run in an infinite loop unless if an administrator disables forced focus & zoom checks
    while True:
        # Get camera IP/hostname, port, username, password, etc.
        # We should always get the settings for each attempt, camera settings may have changed since last check.
        camera = CameraSettings.filter_by_camera_id(camera_id)

        # Stop if camera is not found in the database.
        if camera is None:
            raise Exception("Camera {} not found in database".format(camera_id))

        # Check if the camera is enabled to be forced focused & zoomed
        if not camera.enable:
            raise Exception("Camera {} enable setting is turned off... exiting".format(camera.camera_id))

        if camera.manufacturer == "Dahua":
            dahua_if = Dahua(camera.camera_label, camera_id, camera.username, camera.password, camera.hostname,
                             camera.port,
                             camera.focus, camera.zoom, https=False)
            try:
                dahua_if.set_focus_and_zoom()
            except Exception as ex:
                logging.error("Could not set camera focus and zoom.")
                logging.exception(ex)

                # Send to each email address specified in the Notifications settings page
                if camera.notify_on_failed_interval_check:
                    email.body = "⚠️ Failed to force focus and zoom camera.\n\n" \
                                 "Label: {}\nUID: {}\nException: {}\n".format(camera.camera_label, camera.camera_id, ex)

                    email.send()

            # Sleep
            time.sleep(camera.focus_zoom_interval_check)
        else:
            raise Exception("Unsupported camera manufacturer '{}' for camera ID# {}.".format(camera.manufacturer,
                                                                                             camera.camera_id))


def send_alert(custom_alert_id: int, alpr_group_id: int):
    # Make the application context available here. This function is forked into a separate process and the database
    # connections needs to be reintroduced.
    app = create_app(app_config)
    app.app_context().push()

    # Email
    email = Email()
    email.tag = Tag.ALERT.value

    try:
        custom_alert = CustomAlert.filter_by_id(custom_alert_id)
        custom_alert_alpr_group = ALPRGroup.filter_by_id(custom_alert.alpr_group_id)
        alpr_group = ALPRGroup.filter_by_id(alpr_group_id)

        if custom_alert:
            email.subject = "{} Match!".format(custom_alert.license_plate)

            report_settings = GeneralSettings.get_settings()
            submitted_user = User.find_by_id(custom_alert.submitted_by_user_id)
            submitted_user_profile = UserProfile.find_by_user_id(custom_alert.submitted_by_user_id)

            # Add a publicly accessible URL
            email.body = "🚨 Custom Alert: {}\n\n{}\nLocation/Agent: {}\nCamera: {}\nOrganization: {}\n".format(
                custom_alert.license_plate, custom_alert.description, custom_alert_alpr_group.web_server_config['agent_label'],
                custom_alert_alpr_group.web_server_config['camera_label'], report_settings.org_name)

            # Send email alert to submitter first
            if helper.are_valid_email_recipients(submitted_user.email):
                email.recipients = submitted_user.email
                email.send()

            sms = SMS()
            sms.msg = "🚨 Custom Alert: {}\n\n{}\n\nLocation/Agent: {}\n\nCamera: {}\n\nOrganization: {}\n\n" \
                      "OpenALPR-Webhook".format(custom_alert.license_plate, custom_alert.description,
                                                custom_alert_alpr_group.web_server_config['agent_label'],
                                                custom_alert_alpr_group.web_server_config['camera_label'],
                                                report_settings.org_name)

            # Send sms alert to submitter first
            if helper.are_valid_sms_recipients(submitted_user_profile.phone):
                sms.recipients = submitted_user_profile.phone
                sms.send()

            # Send to additional recipients
            if custom_alert.notify_user_ids is not None:
                for _id in custom_alert.notify_user_ids:
                    user = User.find_by_id(_id)
                    user_profile = UserProfile.find_by_user_id(_id)
                    if user is not None:
                        if helper.are_valid_email_recipients(user.email):
                            email.recipients = user.email
                            email.send()
                    if user_profile is not None:
                        if helper.are_valid_sms_recipients(user_profile.phone):
                            sms.recipients = user_profile.phone
                            sms.send()
            else:
                logging.exception("ALPR Group #{} was not found in the database.".format(custom_alert.alpr_group_id))
                raise Exception("ALPR Group #{} was not found in the database.".format(custom_alert.alpr_group_id))
        else:
            logging.exception("Custom alert #{} was not found in the database.".format(custom_alert_id))
            raise Exception("Custom alert #{} was not found in the database.".format(custom_alert_id))

    except Exception as ex:
        logging.exception(ex)
