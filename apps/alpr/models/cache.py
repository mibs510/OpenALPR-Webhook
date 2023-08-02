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

import logging
import os
import pathlib
import platform
from datetime import datetime, timedelta

from markupsafe import Markup

from apps import db
from sqlalchemy.exc import SQLAlchemyError

from apps.alpr import beautify
from apps.alpr.enums import ChartType
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.alpr_alert import ALPRAlert
from apps.alpr.models.settings import AgentSettings, CameraSettings
from apps.alpr.models.vehicle import Vehicle
from apps.exceptions.exception import InvalidUsage
from sqlalchemy_json import NestedMutableJson


class Cache(db.Model):
    __bind_key__ = 'cache'
    __tablename__ = 'Cache'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    all_time_plates_captured = db.Column(db.Integer, default=0)
    all_time_alerts = db.Column(db.Integer, default=0)
    all_time_custom_alerts = db.Column(db.Integer, default=0)
    all_time_vehicles = db.Column(db.Integer, default=0)
    month = db.Column(NestedMutableJson,
                      default=[{"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}},
                               {"license_plates_captured": 0, "alerts": 0, "custom_alerts": 0, "vehicles": 0,
                                "cameras": {}, "regions": {}}]
                      )

    def __init__(self, year=datetime.now().year, month=datetime.now().month):
        self.year = year
        # Not to be confused with month = db.Column()
        # Should be an integer from 1 - 12
        self._month_ = month

    @classmethod
    def filter_by_year(cls, year=datetime.now().year) -> "Cache":
        # CHeck to see if a row/year exists
        cache = cls.query.filter_by(year=year).first()

        # Create a new row/year if it doesn't exist
        if cache is None:
            cache = Cache(year=year)
            cache.save()

        return cache

    def get_alert_count(self, year: int, month: int) -> int:
        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        return cache.month[month - 1]['alerts']

    def get_combined_alert_count(self, year: int, month: int) -> int:
        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        return cache.month[month - 1]['alerts'] + cache.month[month - 1]['custom_alerts']

    def get_custom_alert_count(self, year: int, month: int) -> int:
        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        return cache.month[month - 1]['custom_alerts']

    def get_all_db_file_sizes(self, raw=False) -> str:
        if raw:
            return str(os.path.getsize("apps/db/alpr_alert.sqlite") +
                       os.path.getsize("apps/db/alpr_group.sqlite") +
                       os.path.getsize("apps/db/vehicle.sqlite"))

        return beautify.human_size(os.path.getsize("apps/db/alpr_alert.sqlite") +
                                   os.path.getsize("apps/db/alpr_group.sqlite") +
                                   os.path.getsize("apps/db/vehicle.sqlite"))

    def get_all_time_alerts_count(self) -> int:
        total_alerts = 0
        alerts = self.query.all()

        for alert in alerts:
            total_alerts += alert.all_time_alerts

        return total_alerts

    def get_all_time_plates_count(self) -> int:
        total_plates_captured = 0
        years = self.query.all()

        for year in years:
            total_plates_captured += year.all_time_plates_captured

        return total_plates_captured

    def get_all_time_vehicle_count(self) -> int:
        total_vehicles = 0
        vehicles = self.query.all()

        for vehicle in vehicles:
            total_vehicles += vehicle.all_time_vehicles

        return total_vehicles

    def get_chart_series(self, chart: ChartType) -> []:
        series = []

        year = datetime.now().year
        # Move to previous month
        last_month = datetime.now().month - 1
        # Move to previous year when needed
        if last_month == 0:
            year -= 1
            last_month = 12

        for i in range(12):
            if chart == ChartType.PLATES_CAPTURED_CHART or chart == ChartType.TOP_SECOND_REGION_CHART:
                # License Plates Captured
                this_month_license_plate_count = self.get_license_plate_count(year, last_month)

                if chart == ChartType.PLATES_CAPTURED_CHART:
                    series.append(this_month_license_plate_count)
                elif chart == ChartType.TOP_SECOND_REGION_CHART:
                    # Top Region
                    this_month_top_second_region_count = self.get_top_second_region_count(year, last_month)
                    series.append(this_month_top_second_region_count)

            elif chart == ChartType.ALERT_CHART:
                # Alerts
                this_month_alert_count = self.get_alert_count(year, last_month)
                series.append(this_month_alert_count)
            elif chart == ChartType.CUSTOM_ALERT:
                this_month_custom_alert_count = self.get_custom_alert_count(year, last_month)
                series.append(this_month_custom_alert_count)

            # Move to previous month
            last_month -= 1
            # Move to previous year when needed
            if last_month == 0:
                year -= 1
                last_month = 12

        return Markup(list(reversed(series)))

    def get_chart_labels(self, chart=None) -> []:
        series = []

        year = datetime.now().year
        # Move to previous month
        month = datetime.now().month - 1
        # Move to previous year when needed

        for i in range(12):
            start_of_month = datetime(year=year, month=month, day=1)

            if chart == ChartType.TOP_SECOND_REGION_CHART:
                pretty_region = beautify.country(self.get_top_second_region(year, month))
                series.append("{} - {}".format(start_of_month.strftime("%b %Y"), pretty_region))
            else:
                series.append(start_of_month.strftime("%b %Y"))

            # Move to previous month
            month -= 1
            # Move to previous year when needed
            if month == 0:
                year -= 1
                month = 12

        return Markup(list(reversed(series)))

    # Thanks to augustomen @stackoverflow.com
    # https://stackoverflow.com/a/13565185
    def get_last_day_of_month(self, any_day: datetime) -> datetime:
        # The day 28 exists in every month. 4 days later, it's always next month
        next_month = any_day.replace(day=28) + timedelta(days=4)
        # subtracting the number of the current day brings us back one month
        return next_month - timedelta(days=next_month.day)

    def get_license_plate_count(self, year: int, month: int) -> int:
        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        return cache.month[month - 1]['license_plates_captured']

    def get_number_of_records(self, raw=False) -> str:
        if raw:
            return str(self.get_all_time_plates_count() +
                       self.get_all_time_alerts_count() +
                       self.get_all_time_vehicle_count())

        return beautify.human_format(self.get_all_time_plates_count() +
                                     self.get_all_time_alerts_count() +
                                     self.get_all_time_vehicle_count())

    def get_quick_stats(self) -> {}:
        response = {}

        # Get the number of plates and alerts for this month
        start_of_month = datetime.today().replace(day=1)
        end_of_month = self.get_last_day_of_month(datetime.now())

        if platform.system() == "Windows":
            response['start_of_month_pretty'] = start_of_month.strftime("%b %e")
            response['end_of_month_pretty'] = end_of_month.strftime("%b %e")
        else:
            response['start_of_month_pretty'] = start_of_month.strftime("%b %-d")
            response['end_of_month_pretty'] = end_of_month.strftime("%b %-d")

        year = datetime.now().year
        month = datetime.now().month
        # Move to previous month
        last_month = datetime.now().month - 1
        # Move to previous year when needed
        if last_month == 0:
            year -= 1
            last_month = 12

        this_month_alert_count = self.get_combined_alert_count(year, month)
        this_month_license_plate_count = self.get_license_plate_count(year, month)
        # print("this_month_license_plate_count = {}".format(this_month_license_plate_count))
        this_month_top_second_region = self.get_top_second_region(year, month)
        # print("this_month_top_second_region = {}".format(this_month_top_second_region))
        this_month_top_second_region_count = self.get_top_second_region_count(year, month)
        # print("this_month_top_second_region_count = {}".format(this_month_top_second_region_count))

        response['this_month_alert_count'] = this_month_alert_count
        response['this_month_rekor_alert_count'] = self.get_alert_count(year, month)
        response['this_month_custom_alert_count'] = self.get_custom_alert_count(year, month)
        response['this_month_license_plate_count'] = this_month_license_plate_count
        response['this_month_top_second_region'] = beautify.country(this_month_top_second_region)
        response['this_month_top_second_region_count'] = this_month_top_second_region_count

        last_month_alert_count = self.get_alert_count(year, last_month)
        last_month_license_plate_count = self.get_license_plate_count(year, last_month)
        # print("last_month_license_plate_count = {}".format(last_month_license_plate_count))
        last_month_top_second_region = self.get_top_second_region(year, last_month)
        # print("last_month_top_second_region = {}".format(last_month_top_second_region))
        last_month_top_second_region_count = self.get_region_count(year, last_month, this_month_top_second_region)
        # print("last_month_top_second_region_count = {}".format(last_month_top_second_region_count))

        response['last_month_alert_count'] = last_month_alert_count
        response['last_month_license_plate_count'] = last_month_license_plate_count
        response['last_month_top_second_region'] = beautify.country(last_month_top_second_region)
        response['last_month_top_second_region_count'] = last_month_top_second_region_count

        # Calculate Month-To-Month for the number of plates captured
        if last_month_license_plate_count != 0:
            mtm_license_plates_percent = ((this_month_license_plate_count / last_month_license_plate_count) - 1) * 100
            mtm_license_plates_percent = round(mtm_license_plates_percent, 1)
            # Determine the color/class of the percentage
            if mtm_license_plates_percent < 0:
                response['this_month_license_plates_mtm_class'] = "text-danger"
                response['this_month_license_plates_mtm_svg_html_arrow'] = beautify.get_negative_mtm_svg_html_arrow()
            elif mtm_license_plates_percent == 0:
                response['this_month_license_plates_mtm_class'] = ""
            elif mtm_license_plates_percent > 0:
                response['this_month_license_plates_mtm_class'] = "text-success"
                response['this_month_license_plates_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        elif last_month_license_plate_count == 0 and this_month_license_plate_count != 0:
            mtm_license_plates_percent = 100
            response['this_month_license_plates_mtm_class'] = "text-success"
            response['this_month_license_plates_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        else:
            mtm_license_plates_percent = 0
            response['this_month_license_plates_mtm_class'] = ""
            response['this_month_license_plates_mtm_svg_html_arrow'] = ""

        response["this_month_license_plates_mtm_percent"] = mtm_license_plates_percent

        # Calculate Month-To-Month for the number of alerts captured
        if last_month_alert_count != 0:
            mtm_alerts_percent = ((this_month_alert_count / last_month_alert_count) - 1) * 100
            mtm_alerts_percent = round(mtm_alerts_percent, 1)
            # Determine the color/class of the percentage
            if mtm_alerts_percent < 0:
                response['this_month_alerts_mtm_class'] = "text-danger"
                response['this_month_alerts_mtm_svg_html_arrow'] = beautify.get_negative_mtm_svg_html_arrow()
            elif mtm_alerts_percent == 0:
                response['this_month_alerts_mtm_class'] = ""
            elif mtm_alerts_percent > 0:
                response['this_month_alerts_mtm_class'] = "text-success"
                response['this_month_alerts_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        elif last_month_alert_count == 0 and this_month_alert_count != 0:
            mtm_alerts_percent = 100
            response['this_month_alerts_mtm_class'] = "text-success"
            response['this_month_alerts_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        else:
            mtm_alerts_percent = 0
            response['this_month_alerts_mtm_class'] = ""
            response['this_month_alerts_mtm_svg_html_arrow'] = ""

        response["this_month_alerts_mtm_percent"] = mtm_alerts_percent

        # Calculate Month-To-Month for the top second region
        if last_month_top_second_region != "N/A" and this_month_top_second_region != "N/A":
            if last_month_top_second_region == this_month_top_second_region:
                mtm_region_percent = \
                    ((this_month_top_second_region_count / last_month_top_second_region_count) - 1) * 100
                mtm_region_percent = round(mtm_region_percent, 1)
                # Determine the color/class of the percentage
                if mtm_region_percent < 0:
                    response['this_month_top_second_region_mtm_class'] = "text-danger"
                    response['this_month_top_second_region_mtm_svg_html_arrow'] = \
                        beautify.get_negative_mtm_svg_html_arrow()
                elif mtm_region_percent == 0:
                    response['this_month_top_second_region_mtm_class'] = ""
                elif mtm_region_percent > 0:
                    response['this_month_top_second_region_mtm_class'] = "text-success"
                    response['this_month_top_second_region_mtm_svg_html_arrow'] = \
                        beautify.get_positive_mtm_svg_html_arrow()
            else:
                mtm_region_percent = 100
                response['this_month_top_second_region_mtm_class'] = "text-success"
                response['this_month_top_second_region_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        elif last_month_top_second_region_count == 0 and this_month_top_second_region_count != 0:
            mtm_region_percent = 100
            response['this_month_top_second_region_mtm_class'] = "text-success"
            response['this_month_top_second_region_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        else:
            mtm_region_percent = 0
            response['this_month_top_second_region_mtm_class'] = ""
            response['this_month_top_second_region_mtm_svg_html_arrow'] = ""

        response["this_month_top_second_region_mtm_percent"] = mtm_region_percent

        return response

    def get_regions(self, year: int, month: int) -> {}:
        cache = self.filter_by_year(year)
        if cache is None:
            return {}

        return cache.month[month - 1]['regions']

    def get_top_cameras(self, n=3) -> {}:
        cache = self.filter_by_year()
        month = datetime.now().month
        dic = cache.month[month - 1]['cameras']

        cameras = []
        i = 0
        # Resolve camera ids to labels
        for key, value in dic.items():
            # Limit the amount of cameras to n
            if i >= n:
                break
            # camera_id, label, count, latitude, longitude
            cameras.append((key, CameraCache.get_camera_label(key), value, CameraCache.get_camera_gps_latitude(key),
                            CameraCache.get_camera_gps_longitude(key)))
            i += 1

        return cameras

    def get_us_map_regions(self, n=8) -> []:
        regions = []

        year = datetime.now().year
        # Move to previous month
        month = datetime.now().month - 1
        # Move to previous year when needed
        if month == 0:
            year -= 1
            month = 12

        last_month_license_plate_count = self.get_license_plate_count(year, month)
        last_month_regions = self.get_regions(year, month)

        for region in last_month_regions:
            regions.append({"name": beautify.country(region), "count": last_month_regions[region],
                            "percent": (beautify.round_percentage(
                                (last_month_regions[region] / last_month_license_plate_count) * 100, symbol=False)),
                            "total": last_month_license_plate_count, "flag_uri": beautify.get_flag_uri(region)})

        if n != 0:
            return regions[:n]
        else:
            return regions

    def get_us_map_series(self) -> []:
        year = datetime.now().year
        # Move to previous month
        month = datetime.now().month - 1
        # Move to previous year when needed
        if month == 0:
            year -= 1
            month = 12

        regions = self.get_regions(year, month)
        us_regions = []

        if len(regions) == 0:
            return Markup([])

        for key in regions:
            if str(key).split("-")[0] == "us":
                us_regions.append([str(key).split("-")[1].upper(), regions[key]])

        return Markup(us_regions)

    def get_region_count(self, year: int, month: int, region: str) -> int:
        if region == "N/A":
            return 0

        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        return int(cache.month[month - 1]['regions'].get(region))

    def get_top_region(self, year, month) -> str:
        cache = self.filter_by_year(year)
        if cache is None:
            return "N/A"

        length = len(list(cache.month[month - 1]['regions']))
        return str(list(cache.month[month - 1]['regions'].keys())[0]) if length != 0 else "N/A"

    def get_top_second_region(self, year, month) -> str:
        cache = self.filter_by_year(year)
        if cache is None:
            return "N/A"

        length = len(list(cache.month[month - 1]['regions']))
        return str(list(cache.month[month - 1]['regions'].keys())[1]) if length > 1 else "N/A"

    def get_top_region_count(self, year: int, month: int) -> int:
        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        length = len(list(cache.month[month - 1]['regions']))
        return int(list(cache.month[month - 1]['regions'].values())[0]) if length != 0 else 0

    def get_top_second_region_count(self, year: int, month: int) -> int:
        cache = self.filter_by_year(year)
        if cache is None:
            return 0

        length = len(list(cache.month[month - 1]['regions']))
        return int(list(cache.month[month - 1]['regions'].values())[1]) if length > 1 else 0

    def init(self):
        try:
            # Get the number of plates from the previous 11 months
            # Monday - Sunday
            # now: 2023-01-16 10:02:43.651522
            # start_of_week: 2023-01-16 00:00:00
            # end_of_week: 2023-01-22 23:59:59
            now = datetime.now()
            month = now.month
            year = now.year

            alpr_group = ALPRGroup()
            alpr_alert = ALPRAlert()
            vehicle = Vehicle()

            for i in range(12):
                # Get the row corresponding to this year or create it
                cache = self.filter_by_year(year)

                start_of_month = datetime(year=year, month=month, day=1, hour=0, minute=0, second=0)
                end_of_month = self.get_last_day_of_month(datetime(year=year, month=month, day=1, hour=23, minute=59,
                                                                   second=59))
                start_of_month_timestamp = start_of_month.timestamp()
                end_of_month_timestamp = end_of_month.timestamp()

                alpr_group.start_of_month_timestamp = start_of_month_timestamp
                alpr_group.end_of_month_timestamp = end_of_month_timestamp
                alpr_alert.start_of_month_timestamp = start_of_month_timestamp
                alpr_alert.end_of_month_timestamp = end_of_month_timestamp
                vehicle.start_of_month_timestamp = start_of_month_timestamp
                vehicle.end_of_month_timestamp = end_of_month_timestamp

                # License Plates
                this_month_license_plates = alpr_group.filter_epoch_start()
                this_month_license_plate_count = 0 if this_month_license_plates is None else len(
                    this_month_license_plates)

                # Alerts
                this_month_alerts = alpr_alert.filter_epoch_time()
                this_month_alert_count = 0 if this_month_alerts is None else len(this_month_alerts)

                # Vehicles
                this_month_vehicles = vehicle.filter_epoch_start()
                this_month_vehicle_count = 0 if this_month_vehicles is None else len(this_month_vehicles)

                # Regions
                this_month_regions = alpr_group.get_all_regions()

                # Cameras and counts
                this_month_cameras_and_counts = alpr_group.get_cameras_and_counts()

                # Agent UIDs for settings
                this_month_agent_uids = alpr_group.get_all_agent_uids()

                # Add camera_ids into cache and settings along with the most updated labels
                for camera_id, count in this_month_cameras_and_counts.items():
                    camera_cache = CameraCache.filter_by_camera_id(camera_id)
                    camera_settings = CameraSettings.filter_by_camera_id(camera_id)
                    camera_label = ALPRGroup.get_latest_camera_label(camera_id)
                    camera_gps_latitude = ALPRGroup.get_latest_camera_gps_latitude(camera_id)
                    camera_gps_longitude = ALPRGroup.get_latest_camera_gps_longitude(camera_id)
                    camera_country = ALPRGroup.get_latest_camera_country(camera_id)

                    # Cache
                    if camera_cache is None:
                        camera_cache = CameraCache(camera_id, camera_label)
                    else:
                        camera_cache.camera_label = camera_label

                    # Update user definable values regardless if the camera was found in the cache or not
                    camera_cache.gps_latitude = camera_gps_latitude
                    camera_cache.gps_longitude = camera_gps_longitude
                    camera_cache.country = camera_country
                    # Save it
                    camera_cache.save()

                    # Settings
                    if camera_settings is None:
                        camera_settings = CameraSettings(camera_id, camera_label)
                        camera_settings.created = datetime.fromtimestamp(
                            ALPRGroup.get_oldest_camera_epoch_start(camera_id) / 1000)
                    else:
                        camera_settings.camera_label = camera_label
                    camera_settings.save()

                # Add agent_uids into settings and cache
                for agent_uid, agent_label in this_month_agent_uids.items():
                    agent_settings = AgentSettings.filter_by_agent_uid(agent_uid)
                    agent_cache = AgentCache.filter_by_agent_uid(agent_uid)
                    if agent_settings is None:
                        agent_settings = AgentSettings(agent_uid, alpr_group.get_latest_agent_label(agent_uid))
                        agent_settings.created = \
                            datetime.fromtimestamp(ALPRGroup.get_oldest_agent_epoch_start(agent_uid) / 1000)
                        agent_settings.save()
                    if agent_cache is None:
                        agent_cache = AgentCache(agent_uid, alpr_group.get_latest_agent_label(agent_uid))

                    # These can be updated, so it's best to always overwrite them on each occurrence
                    agent_cache.agent_version = alpr_group.get_latest_agent_version(agent_uid)
                    agent_cache.agent_type = alpr_group.get_latest_agent_type(agent_uid)
                    agent_cache.save()

                # Populate cache
                cache.all_time_plates_captured += this_month_license_plate_count
                cache.all_time_alerts += this_month_alert_count
                cache.all_time_vehicles += this_month_vehicle_count
                cache.month[month - 1]['license_plates_captured'] = this_month_license_plate_count
                cache.month[month - 1]['alerts'] = this_month_alert_count
                cache.month[month - 1]['vehicles'] = this_month_vehicle_count
                cache.month[month - 1]['cameras'] = this_month_cameras_and_counts
                cache.month[month - 1]['regions'] = this_month_regions

                # Save it in the db
                self.save()

                # Move to previous month
                month = month - 1
                # Move to previous year when needed
                if month == 0:
                    year = year - 1
                    month = 12

        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return


class AgentCache(db.Model):
    __bind_key__ = 'cache'
    __tablename__ = 'AgentCache'

    id = db.Column(db.Integer, primary_key=True)
    agent_uid = db.Column(db.Integer)
    agent_label = db.Column(db.String)
    agent_version = db.Column(db.Integer)
    agent_type = db.Column(db.Integer)

    def __init__(self, agent_uid: int, agent_label: str):
        self.agent_uid = agent_uid
        self.agent_label = agent_label

    @classmethod
    def filter_by_agent_uid(cls, _agent_uid: str) -> "AgentCache":
        # Check to see if a row/agent_id exists
        return cls.query.filter_by(agent_uid=_agent_uid).first()

    @classmethod
    def get_agent_label(cls, _agent_uid: str) -> "AgentCache":
        agent = cls.query.filter_by(agent_uid=_agent_uid).first()
        return agent.agent_label

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)


class CameraCache(db.Model):
    __bind_key__ = 'cache'
    __tablename__ = 'CameraCache'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer)
    camera_label = db.Column(db.String)
    gps_latitude = db.Column(db.Integer)
    gps_longitude = db.Column(db.Integer)
    country = db.Column(db.String)

    def __init__(self, camera_id: int, camera_label: str):
        self.camera_id = camera_id
        self.camera_label = camera_label

    @classmethod
    def filter_by_camera_id(cls, _camera_id: int) -> "CameraCache":
        # Check to see if a row/camera_id exists
        return cls.query.filter_by(camera_id=_camera_id).first()

    @classmethod
    def filter_by_id_and_beautify(cls, _camera_id: int) -> "CameraCache":
        camera = cls.query.filter_by(camera_id=_camera_id).first()

        if camera:
            camera.country = beautify.name(camera.country)

        return camera

    @classmethod
    def get_camera_label(cls, _camera_id: int) -> "CameraCache":
        camera = cls.query.filter_by(camera_id=_camera_id).first()
        return camera.camera_label

    @classmethod
    def get_camera_gps_latitude(cls, _camera_id: int) -> "CameraCache":
        camera = cls.query.filter_by(camera_id=_camera_id).first()
        return camera.gps_latitude

    @classmethod
    def get_camera_gps_longitude(cls, _camera_id: int) -> "CameraCache":
        camera = cls.query.filter_by(camera_id=_camera_id).first()
        return camera.gps_longitude

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
