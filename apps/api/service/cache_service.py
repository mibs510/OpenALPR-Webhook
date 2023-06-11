from rq import Retry
import json
import logging
from datetime import datetime

from apps import default_q
from apps.alpr.enums import DataType
from apps.alpr.models.cache import Cache, CameraCache
from apps.alpr.models.custom_alert import CustomAlert
from apps.alpr.models.settings import AgentSettings, CameraSettings
from apps.alpr.queue import send_alert
from apps.messages import Messages

message = Messages.message


class CacheService:
    foreign_id = None
    now = datetime.now()
    this_year = now.year
    # From 0 - 11 not 1 - 12
    this_month = now.month - 1

    def __init__(self, request_json: json, foreign_id: int):
        self.foreign_id = foreign_id
        self.request = request_json

        # Load the cache if it already exists
        self.cache = Cache.filter_by_year()

        # Create a row if the year doesn't exist
        if not self.cache:
            self.cache = Cache()
    
    def update(self):
        try:
            if self.request['data_type'] == DataType.GROUP:
                # Increase counters
                self.cache.all_time_plates_captured += 1
                self.cache.month[self.this_month]['license_plates_captured'] += 1
                # Objects
                self.cache.month[self.this_month]['cameras'] = \
                    self.increase_dict_value_count("cameras", self.request['camera_id'])

                self.cache.month[self.this_month]['regions'] = \
                    self.increase_dict_value_count("regions", self.request['best_region'])

                # Cache
                camera_id_cache = CameraCache.filter_by_camera_id(self.request['camera_id'])
                if camera_id_cache is None:
                    camera_id_cache = CameraCache(int(self.request['camera_id']),
                                                  self.request['web_server_config']['camera_label'])
                else:
                    # Always overwrite the user definable values, they may have changed
                    camera_id_cache.camera_label = self.request['web_server_config']['camera_label']
                    camera_id_cache.gps_latitude = self.request['gps_latitude']
                    camera_id_cache.gps_longitude = self.request['gps_longitude']
                    camera_id_cache.country = self.request['country']
                camera_id_cache.save()

                # Settings

                # Agents
                agent_uid = AgentSettings.filter_by_agent_uid(self.request['agent_uid'])

                if agent_uid is None:
                    agent_uid = AgentSettings(self.request['agent_uid'], self.request['web_server_config']['agent_label'])
                else:
                    # Always overwrite the label, it may have changed
                    agent_uid.agent_label = self.request['web_server_config']['agent_label']
                agent_uid.save()

                # Cameras
                camera_id = CameraSettings.filter_by_camera_id(self.request['camera_id'])

                if camera_id is None:
                    camera_id = CameraSettings(self.request['camera_id'], self.request['web_server_config']['camera_label'])
                else:
                    # Always overwrite the label, it may have changed
                    camera_id.camera_label = self.request['web_server_config']['camera_label']
                camera_id.save()

                # Check to see if we need to send an alert
                custom_alert = CustomAlert.filter_by_license_plate(self.request['best_plate_number'])
                if custom_alert:
                    # Send the id to the custom alert to the queue to notify recipients
                    default_q.enqueue(send_alert, custom_alert.id)

            elif self.request['data_type'] == DataType.ALERT:
                self.cache.all_time_alerts += 1
                self.cache.month[self.this_month]['alerts'] += 1
            elif self.request['data_type'] == DataType.VEHICLE:
                self.cache.all_time_vehicles += 1
                self.cache.month[self.this_month]['vehicles'] += 1

            # Update/save the cache
            self.cache.save()

            # Prevent circular/infinite loop import
            from apps.alpr.queue import download_plate_image

            # Send it to the queue to download the uuid.jpg from the origin agent
            default_q.enqueue(download_plate_image, self.request['agent_uid'], self.request['best_uuid'],
                              self.request['data_type'], self.foreign_id, retry=Retry(max=5, interval=60))

            return self.cache
        except Exception as ex:
            logging.exception(ex)
            raise Exception(ex)

    def increase_dict_value_count(self, dict_index: str, key: str) -> {}:
        keys_values = dict(self.cache.month[self.this_month][dict_index])
        if key in keys_values.keys():
            # Increase the counter/value if the key is already in the dictionary
            keys_values[key] += 1
        else:
            # Add another key value pair to the dictionary if the pair does not already exist
            keys_values.update({key: 1})

        # Sort the dictionary from greatest to least
        return dict(sorted(keys_values.items(), key=lambda count: count[1], reverse=True))
