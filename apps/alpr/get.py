import os.path
import platform
from datetime import datetime, timedelta

from markupsafe import Markup
from unqlite import UnQLite

import apps.alpr as alpr
import apps.alpr.beautify as beautify
import apps.alpr.cache as Cache
import apps.alpr.util as util


class Get:
    now = datetime.now()
    month = now.month
    year = now.year

    def __init__(self):
        self.cache = Cache.Cache()

    def all_cameras(self, filtered_collection) -> {}:
        if filtered_collection is None:
            return {}

        cameras = []

        # Add every camera for that month onto a list
        for record in filtered_collection:
            cameras.append(record['web_server_config']['camera_label'])

        # Go through each region and get a count
        dictionary = {}
        for camera in cameras:
            dictionary[camera] = cameras.count(camera)

        # Sort the dictionary from greatest to least
        return dict(sorted(dictionary.items(), key=lambda count: count[1], reverse=True))

    def all_dbs_file_sizes(self) -> str:
        return beautify.human_size(os.path.getsize(alpr.__alpr_alert_db__) + os.path.getsize(alpr.__alpr_group_db__) +
                               os.path.getsize(alpr.__vehicle_db__))

    def chart_series(self, chart) -> []:
        series = []

        this_year = self.year
        # Move to previous month
        last_month = self.month - 1
        # Move to previous year when needed
        if last_month == 0:
            this_year -= 1
            last_month = 12

        for i in range(12):
            if chart == "plates-captured-chart" or chart == "top-region-chart":
                # License Plates Captured
                this_month_license_plate_count = self.cache.get_license_plate_count(this_year, last_month)

                if chart == "plates-captured-chart":
                    series.append(this_month_license_plate_count)
                elif chart == "top-region-chart":
                    # Top Region
                    this_month_top_region_count = self.cache.get_top_region_count(this_year, last_month)
                    series.append(this_month_top_region_count)

            elif chart == "alert-chart":
                # Alerts
                this_month_alert_count = self.cache.get_alert_count(this_year, last_month)
                series.append(this_month_alert_count)

            # Move to previous month
            last_month -= 1
            # Move to previous year when needed
            if last_month == 0:
                this_year -= 1
                last_month = 12

        return Markup(list(reversed(series)))

    def chart_labels(self, chart=None) -> []:
        series = []

        this_year = self.year
        # Move to previous month
        last_month = self.month - 1

        for i in range(12):
            start_of_month = datetime(year=this_year, month=last_month, day=1)

            if chart == "top-region-chart":
                pretty_region = beautify.country(self.cache.get_top_region(this_year, last_month))
                series.append("{} - {}".format(start_of_month.strftime("%b %Y"), pretty_region))
            else:
                series.append(start_of_month.strftime("%b %Y"))

            # Move to previous month
            last_month -= 1
            # Move to previous year when needed
            if last_month == 0:
                this_year -= 1
                last_month = 12

        return Markup(list(reversed(series)))

    def collection(self, database="alpr_group") -> {}:
        db = alpr.__alpr_group_db__
        table = "alpr_group"

        if database == "alert":
            db = alpr.__alpr_alert_db__
            table = "alpr_alert"
        elif database == "cache":
            db = alpr.__cache_db__
            table = "cache"
        elif database == "vehicle":
            db = alpr.__vehicle_db__
            table = "vehicle"

        db_connection = UnQLite(db)
        return db_connection.collection(table)

    # Thanks to augustomen @stackoverflow.com
    # https://stackoverflow.com/a/13565185
    def last_day_of_month(self, any_day):
        # The day 28 exists in every month. 4 days later, it's always next month
        next_month = any_day.replace(day=28) + timedelta(days=4)
        # subtracting the number of the current day brings us back one month
        return next_month - timedelta(days=next_month.day)

    def number_of_records(self) -> str:
        return beautify.human_format(self.cache.get_all_time_count("all_time_plates_captured") +
                                     self.cache.get_all_time_count("all_time_alerts") +
                                     self.cache.get_all_time_count("all_time_vehicles"))

    def quick_stats(self) -> {}:
        response = {}

        # Get the number of plates and alerts for this month
        start_of_month = datetime.today().replace(day=1)
        end_of_month = self.last_day_of_month(self.now)

        if platform.system() == "Windows":
            response['start_of_month_pretty'] = start_of_month.strftime("%b %e")
            response['end_of_month_pretty'] = end_of_month.strftime("%b %e")
        else:
            response['start_of_month_pretty'] = start_of_month.strftime("%b %-d")
            response['end_of_month_pretty'] = end_of_month.strftime("%b %-d")

        this_year = self.year
        # Move to previous month
        last_month = self.month - 1
        # Move to previous year when needed
        if last_month == 0:
            this_year -= 1
            last_month = 12

        this_month_alert_count = self.cache.get_alert_count(self.year, self.month)
        this_month_license_plate_count = self.cache.get_license_plate_count(self.year, self.month)
        this_month_top_region = self.cache.get_top_region(self.year, self.month)
        # print("this_month_top_region = {}".format(this_month_top_region))
        this_month_top_region_count = self.cache.get_top_region_count(self.year, self.month)
        # print("this_month_top_region_count = {}".format(this_month_top_region_count))

        response['this_month_alert_count'] = this_month_alert_count
        response['this_month_license_plate_count'] = this_month_license_plate_count
        response['this_month_top_region'] = beautify.country(this_month_top_region)
        response['this_month_top_region_count'] = this_month_top_region_count

        last_month_alert_count = self.cache.get_alert_count(this_year, last_month)
        last_month_license_plate_count = self.cache.get_license_plate_count(this_year, last_month)
        last_month_top_region = self.cache.get_top_region(this_year, last_month)
        # print("last_month_top_region = {}".format(last_month_top_region))
        last_month_top_region_count = self.cache.get_region_count(this_year, last_month, this_month_top_region)
        # print("last_month_top_region_count = {}".format(last_month_top_region_count))

        response['last_month_alert_count'] = last_month_alert_count
        response['last_month_license_plate_count'] = last_month_license_plate_count
        response['last_month_top_region'] = beautify.country(last_month_top_region)
        response['last_month_top_region_count'] = last_month_top_region_count

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

        # Calculate Month-To-Month for the top region
        if last_month_top_region != "N/A" and this_month_top_region != "N/A":
            mtm_region_percent = ((this_month_top_region_count / last_month_top_region_count) - 1) * 100
            mtm_region_percent = round(mtm_region_percent, 1)
            # Determine the color/class of the percentage
            if mtm_region_percent < 0:
                response['this_month_top_region_mtm_class'] = "text-danger"
                response['this_month_top_region_mtm_svg_html_arrow'] = beautify.get_negative_mtm_svg_html_arrow()
            elif mtm_region_percent == 0:
                response['this_month_top_region_mtm_class'] = ""
            elif mtm_region_percent > 0:
                response['this_month_top_region_mtm_class'] = "text-success"
                response['this_month_top_region_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        elif last_month_top_region_count == 0 and this_month_top_region_count != 0:
            mtm_region_percent = 100
            response['this_month_top_region_mtm_class'] = "text-success"
            response['this_month_top_region_mtm_svg_html_arrow'] = beautify.get_positive_mtm_svg_html_arrow()
        else:
            mtm_region_percent = 0
            response['this_month_top_region_mtm_class'] = ""
            response['this_month_top_region_mtm_svg_html_arrow'] = ""

        response["this_month_top_region_mtm_percent"] = mtm_region_percent

        return response

    def record(self, db="group", n=0) -> []:
        collections = self.collection(db)
        return_obj = []
        start = len(collections) - 1
        finish = 0

        # Iterator limit is set to the number of records
        if n != 0:
            finish = start - n

        for i in range(start, finish, -1):
            return_obj.append(collections[i])

        return return_obj

    def regions(self, n=0) -> []:
        rgns = []

        this_year = self.year
        # Move to previous month
        last_month = self.month - 1
        # Move to previous year when needed
        if last_month == 0:
            this_year -= 1
            last_month = 12

        last_month_license_plate_count = self.cache.get_license_plate_count(this_year, last_month)
        last_month_regions = self.cache.get_regions(this_year, last_month)

        for region in last_month_regions:
            rgns.append({"name": beautify.country(region),
                         "count": last_month_regions[region],
                         "percent": (beautify.round_percentage((last_month_regions[region]/
                                                                last_month_license_plate_count) * 100, symbol=False)),
                         "total": last_month_license_plate_count, "flag_uri": beautify.get_flag_uri(region)})

        if n != 0:
            return rgns[:n]
        else:
            return rgns

    def all_regions(self, filtered_collection) -> {}:
        if filtered_collection is None:
            return {}

        regions = []

        # Add every region for that month onto a list
        for record in filtered_collection:
            regions.append(record['best_region'])

        # Go through each region and get a count
        dictionary = {}
        for region in regions:
            dictionary[region] = regions.count(region)

        # Sort the dictionary from greatest to least
        return dict(sorted(dictionary.items(), key=lambda count: count[1], reverse=True))

    def us_map_series(self) -> []:
        this_year = self.year
        # Move to previous month
        last_month = self.month - 1
        # Move to previous year when needed
        if last_month == 0:
            this_year -= 1
            last_month = 12

        regions = self.cache.get_regions(this_year, last_month)
        us_regions = []

        if len(regions) == 0:
            return Markup([])

        for key in regions:
            if str(key).split("-")[0] == "us":
                us_regions.append([str(key).split("-")[1].upper(), regions[key]])

        return Markup(us_regions)
