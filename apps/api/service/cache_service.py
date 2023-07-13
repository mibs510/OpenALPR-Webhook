#  Copyright (c) 2023. Connor McMillan
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#  following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#  products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from rq import Retry
import json
import logging
from datetime import datetime

from apps import default_q
from apps.alpr.enums import DataType
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.cache import Cache, CameraCache
from apps.alpr.models.custom_alert import CustomAlert
from apps.alpr.models.settings import AgentSettings, CameraSettings
from apps.alpr.queue import send_alert
from apps.messages import Messages

message = Messages.message


class CacheService:
    alpr_group_id = None
    now = datetime.now()
    this_year = now.year
    # From 0 - 11 not 1 - 12
    this_month = now.month - 1

    def __init__(self, request_json: json, alpr_group_id: int):
        self.alpr_group_id = alpr_group_id
        self.request = request_json

        # Load the cache if it already exists
        self.cache = Cache.filter_by_year()

        # Create a row if the year doesn't exist
        if not self.cache:
            self.cache = Cache()

    def update(self):
        try:
            data_type = DataType(self.request['data_type'])
            if data_type == DataType.GROUP:
                # Increase counters
                self.cache.all_time_plates_captured += 1
                self.cache.month[self.this_month]['license_plates_captured'] += 1
                # Objects
                self.cache.month[self.this_month]['cameras'] = \
                    self.increase_dict_value_count("cameras", str(self.request['camera_id']))

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
                    # Don't overwrite them back to -1
                    if self.request['gps_latitude'] != -1:
                        camera_id_cache.gps_latitude = self.request['gps_latitude']
                    if self.request['gps_longitude'] != -1:
                        camera_id_cache.gps_longitude = self.request['gps_longitude']
                    camera_id_cache.country = self.request['country']
                camera_id_cache.save()

                # Settings

                # Agents
                agent_uid = AgentSettings.filter_by_agent_uid(self.request['agent_uid'])

                if agent_uid is None:
                    agent_uid = AgentSettings(self.request['agent_uid'],
                                              self.request['web_server_config']['agent_label'])
                else:
                    # Always overwrite the label, it may have changed
                    agent_uid.agent_label = self.request['web_server_config']['agent_label']
                    agent_uid.last_seen = datetime.utcnow()
                agent_uid.save()

                # Cameras
                camera_id = CameraSettings.filter_by_camera_id(self.request['camera_id'])

                if camera_id is None:
                    camera_id = CameraSettings(self.request['camera_id'],
                                               self.request['web_server_config']['camera_label'])
                else:
                    # Always overwrite the label, it may have changed
                    camera_id.camera_label = self.request['web_server_config']['camera_label']
                    camera_id.last_seen = datetime.utcnow()
                camera_id.save()

                # Check to see if we need to send an alert
                custom_alert = CustomAlert.filter_by_license_plate(self.request['best_plate_number'])
                if custom_alert:
                    this_record = ALPRGroup.filter_by_id(self.alpr_group_id)
                    custom_alert_alpr_group_record = ALPRGroup.filter_by_id(custom_alert.alpr_group_id)
                    if this_record:
                        def enqueue():
                            # Send the id to the custom alert to the queue to notify recipients
                            default_q.enqueue(send_alert, custom_alert.id, self.alpr_group_id)
                            # Increase custom_alerts
                            self.cache.all_time_custom_alerts += 1
                            self.cache.month[self.this_month]['custom_alerts'] += 1

                        if custom_alert.region_match:
                            if this_record.best_region == custom_alert_alpr_group_record.best_region:
                                enqueue()
                            else:
                                logging.info("Plate region match is enabled but does not match")
                        else:
                            enqueue()

            elif data_type == DataType.ALERT:
                self.cache.all_time_alerts += 1
                self.cache.month[self.this_month]['alerts'] += 1
            elif data_type == DataType.VEHICLE:
                self.cache.all_time_vehicles += 1
                self.cache.month[self.this_month]['vehicles'] += 1

            # Prevent circular/infinite loop import
            from apps.alpr.queue import download_plate_image

            # Send it to the queue to download the uuid.jpg from the origin agent
            if data_type == DataType.ALERT:
                best_uuid = self.request['group']['best_uuid']
            else:
                best_uuid = self.request['best_uuid']

            default_q.enqueue(download_plate_image, self.request['agent_uid'], best_uuid, self.request['data_type'],
                              self.alpr_group_id)

            # Update/save the cache
            self.cache.save()

            return self.cache
        except Exception as ex:
            logging.exception(ex)
            logging.debug("data_type = {}".format(self.request['data_type']))
            logging.debug(json.dumps(self.request, ensure_ascii=False, indent=4))
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
