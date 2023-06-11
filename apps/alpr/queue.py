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
    email = Email()
    email.tag = "Agent"

    if agent is None:
        logging.info("Agent does not exist.")
        email.subject = "Unknown Agent"
        email.body = "Failed to download high resolution image. Agent does not exist." \
                     "\n\nAgent UID: {}\nIMG UID: {}".format(agent_uid, img_uuid)
        email.send()
        raise Exception("Failed to download a plate image. Agent does not exist.")
    elif agent.enabled:
        try:
            url = "http://{}:{}/img/{}.jpg".format(agent.ip_hostname, agent.port, img_uuid)
            logging.info("Downloading: {}".format(url))
            # Download it
            req = requests.get(url, stream=True)

            if req.status_code == 200:
                # Create a path to save it to
                full_file_path = Path(os.path.abspath(os.path.dirname(__file__) + "../../../") + "/" +
                                      download_folder_name + img_uuid + ".jpg").absolute()
                # Write to disk
                with open(full_file_path, 'wb') as jpg:
                    shutil.copyfileobj(req.raw, jpg)
                logging.info("File downloaded, location: {}".format(full_file_path))
            else:
                logging.info("Failed to download high resolution plate image. HTTP status_code={}".format(
                    req.status_code))
                email.subject = "High Resolution Image Download Failed"
                email.body = "Failed to download high resolution image. HTTP status code from agent was not 200.\n\n" \
                             "Agent UID: {}\nIMG UID: {}\nHTTP Status: {}".format(agent_uid, img_uuid,
                                                                                  req.status_code)
                email.send()
                raise Exception("Failed to download the plate image. HTTP status_code={}".format(req.status_code))

        except Exception as ex:
            logging.info("Failed to download the plate image")
            email.subject = "High Resolution Image Download Failed"
            email.body = "Failed to download high resolution image. Incorrect IP/hostname & port? Make sure" \
                         "OpenALPR-Webhook can access the agent.\n\nAgent UID: {}\nIMG UID: {}\n" \
                         "Exception: {}".format(agent_uid, img_uuid, ex)
            email.send()
            raise Exception(ex)

        # Find the original record
        record = None

        if data_type == DataType.GROUP:
            record = ALPRGroup.filter_by_id(foreign_id)
        elif data_type == DataType.ALERT:
            record = ALPRAlert.filter_by_id(foreign_id)
        elif data_type == DataType.VEHICLE:
            record = Vehicle.filter_by_id(foreign_id)

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
            EmailNotificationSettings.send("App", "Plate Image Save Failed",
                                           "Failed to save plate image into the database."
                                           "\n\nAgent UID: {}\nIMG UID: {}\nException: {}".format(agent_uid, img_uuid,
                                                                                                  ex))
            # Delete the jpg if something happens above
            # if os.path.isfile(full_file_path):
            #     os.remove(full_file_path)

            raise Exception(ex)
    elif not agent.enabled:
        logging.info("Agent is disabled.")


def focus_camera(camera_id: int):
    # Make the application context available here. This function is forked into a separate process and the database
    # connections needs to be reintroduced.
    app = create_app(app_config)
    app.app_context().push()

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
                logging.error("Could not set camera focus and zoom.\nException: {}".format(ex))

            # Sleep
            for second in range(camera.focus_zoom_interval_check * 60):
                time.sleep(1)
        else:
            raise Exception("Unsupported camera manufacturer '{}' for camera ID# {}.".format(camera.manufacturer,
                                                                                             camera.camera_id))


def send_alert(custom_alert_id: int):
    # Make the application context available here. This function is forked into a separate process and the database
    # connections needs to be reintroduced.
    app = create_app(app_config)
    app.app_context().push()

    try:
        custom_alert = CustomAlert.filter_by_id(custom_alert_id)
        alpr_group = ALPRGroup.filter_by_id(custom_alert.alpr_group_id)

        if custom_alert:
            if alpr_group:
                report_settings = GeneralSettings.get_settings()
                submitted_user = User.find_by_id(custom_alert.submitted_by_user_id)
                submitted_user_profile = UserProfile.find_by_user_id(custom_alert.submitted_by_user_id)

                email = Email()
                email.tag = Tag.ALERT
                email.subject = "{} Match! - OpenALPR-Webhook".format(custom_alert.license_plate)
                # Add a publicly accessible URL
                email.body = "🚨 Custom Alert: {}\n\n{}\n\nLocation/Agent: {}\n\nCamera: {}\n\nOrganization: {}\n\n" \
                             "OpenALPR-Webhook".\
                    format(custom_alert.license_plate, custom_alert.description,
                           alpr_group.web_server_config['agent_label'],
                           alpr_group.web_server_config['camera_label'], report_settings.org_name)

                # Send email alert to receipt first
                if helper.are_valid_email_recipients(submitted_user.email):
                    email.recipients = submitted_user.email
                    email.send()

                sms = SMS()
                sms.msg = "🚨 Custom Alert: {}\n\n{}\n\nLocation/Agent: {}\n\nCamera: {}\n\nOrganization: {}\n\n" \
                          "OpenALPR-Webhook".format(custom_alert.license_plate, custom_alert.description,
                                                    alpr_group.web_server_config['agent_label'],
                                                    alpr_group.web_server_config['camera_label'],
                                                    report_settings.org_name)

                # Send email alert to receipt first
                if helper.are_valid_sms_recipients(submitted_user_profile.phone):
                    sms.recipients = submitted_user_profile.phone
                    sms.send()

                # Send to additional recipients
                if custom_alert.notify_user_ids is not None:
                    for id in custom_alert.notify_user_ids:
                        user = User.find_by_id(id)
                        user_profile = UserProfile.find_by_user_id(id)
                        if helper.are_valid_email_recipients(user.email):
                            email.recipients = user.email
                            email.send()
                        if helper.are_valid_sms_recipients(user_profile.phone):
                            sms.recipients = user_profile.phone
                            sms.send()
            else:
                print("ALPR Group #{} was not found in the database.".format(custom_alert.alpr_group_id))
                logging.exception("ALPR Group #{} was not found in the database.".format(custom_alert.alpr_group_id))
                raise Exception("ALPR Group #{} was not found in the database.".format(custom_alert.alpr_group_id))
        else:
            print("Custom alert #{} was not found in the database.".format(custom_alert_id))
            logging.exception("Custom alert #{} was not found in the database.".format(custom_alert_id))
            raise Exception("Custom alert #{} was not found in the database.".format(custom_alert_id))

    except Exception as ex:
        print(ex)
        logging.exception(ex)
