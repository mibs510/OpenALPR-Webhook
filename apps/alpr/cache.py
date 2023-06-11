import json

from unqlite import UnQLite

import apps.alpr as alpr
import apps.alpr.get as Get
import apps.alpr.util as util

from datetime import datetime


class Cache:
    def __init__(self):
        cache_db = alpr.__cache_db__
        cache = UnQLite(cache_db)
        self.collection = cache.collection("cache")

        self.now = datetime.now()
        self.month = self.now.month
        self.year = self.now.year

    def append_year(self, year) -> None:
        cache_json_file = open(alpr.__cache_json__)
        cache_json = json.load(cache_json_file)
        cache_json['year'] = year

        self.collection.store(json.loads(json.dumps(cache_json)))

    def check_year(self, year) -> None:
        year_in_cache = False
        for years in self.collection.all():
            if years['year'] == year:
                year_in_cache = True

        if not year_in_cache:
            self.append_year(year)

    def get_alert_count(self, year, month) -> int:
        for row in self.collection:
            if row['year'] == year:
                return row['month'][month - 1]['alerts']

    def get_all_time_count(self, key) -> int:
        count = 0
        for row in self.collection:
            count += row[key]

        return count

    def get_license_plate_count(self, year, month) -> int:
        for row in self.collection:
            if row['year'] == year:
                return row['month'][month - 1]['license_plates_captured']

    def get_regions(self, year, month) -> {}:
        for row in self.collection:
            if row['year'] == year:
                return row['month'][month - 1]['regions']

    def get_region_count(self, year, month, region) -> int:
        if region == "N/A":
            return 0
        for row in self.collection:
            if row['year'] == year:
                count = row['month'][month - 1]['regions'].get(region)
                if count is not None:
                    return int((row['month'][month - 1]['regions'].get(region)))
                else:
                    return 0

    def get_top_region(self, year, month) -> str:
        for row in self.collection:
            if row['year'] == year:
                if len(list(row['month'][month - 1]['regions'])) != 0:
                    return str(list(row['month'][month - 1]['regions'].keys())[0])
                else:
                    return "N/A"

    def get_top_region_count(self, year, month) -> int:
        for row in self.collection:
            if row['year'] == year:
                if len(list(row['month'][month - 1]['regions'])) != 0:
                    return int(list(row['month'][month - 1]['regions'].values())[0])
                else:
                    return 0

    def init(self) -> str:
        alpr_group_db = alpr.__alpr_group_db__
        alpr_groups = UnQLite(alpr_group_db)
        alpr_group_collection = alpr_groups.collection("alpr_group")

        alpr_alert_db = alpr.__alpr_alert_db__
        alpr_alerts = UnQLite(alpr_alert_db)
        alpr_alert_collection = alpr_alerts.collection("alpr_alert")

        vehicle_db = alpr.__vehicle_db__
        vehicles = UnQLite(vehicle_db)
        vehicle_collection = vehicles.collection("vehicle")

        # Get the number of plates from the previous 11 months
        # Monday - Sunday
        # now: 2023-01-16 10:02:43.651522
        # start_of_week: 2023-01-16 00:00:00
        # end_of_week: 2023-01-22 00:00:00
        now = datetime.now()
        month = now.month
        this_year = now.year

        for i in range(12):
            start_of_month = datetime(year=this_year, month=month, day=1)
            end_of_month = Get.Get().last_day_of_month(datetime(year=this_year, month=month, day=1))
            epoch_start_of_month = start_of_month.timestamp()
            epoch_end_of_month = end_of_month.timestamp()

            # License Plates
            this_month_license_plates = alpr_group_collection.filter(
                lambda start: epoch_start_of_month <= start['epoch_start'] / 1000 <= epoch_end_of_month)
            this_month_license_plate_count = 0 if this_month_license_plates is None else len(this_month_license_plates)

            # Alerts
            this_month_alerts = alpr_alert_collection.filter(
                lambda start: epoch_start_of_month <= start['epoch_time'] / 1000 <= epoch_end_of_month)
            this_month_alert_count = 0 if this_month_alerts is None else len(this_month_alerts)

            # Vehicles
            this_month_vehicles = vehicle_collection.filter(
                lambda start: epoch_start_of_month <= start['epoch_start'] / 1000 <= epoch_end_of_month)
            this_month_vehicle_count = 0 if this_month_vehicles is None else len(this_month_vehicles)

            # All Regions
            this_month_regions = Get.Get().all_regions(this_month_license_plates)

            # All camera
            cameras = Get.Get().all_cameras(this_month_license_plates)

            # Populate cache
            for year in self.collection:
                if year['year'] == this_year:
                    year['all_time_plates_captured'] += this_month_license_plate_count
                    year['all_time_alerts'] += this_month_alert_count
                    year['all_time_vehicles'] += this_month_vehicle_count
                    year['month'][month - 1]['license_plates_captured'] = this_month_license_plate_count
                    year['month'][month - 1]['alerts'] = this_month_alert_count
                    year['month'][month - 1]['regions'] = this_month_regions
                    year['month'][month - 1]['camera'] = cameras
                    self.collection.update(year['__id'], year)

            # Move to previous month
            month = month - 1
            # Move to previous year when needed
            if month == 0:
                this_year = this_year - 1
                month = 12

        util.save_to_json(self.collection.all(), "cache_exported")
        return "Cache initiated!"

    def increase_dict_value_count(self, dict_index, key) -> {}:
        for row in self.collection:
            if row['year'] == self.year:
                keys_values = dict(row['year']['month'][self.month - 1][dict_index])
                if key in keys_values.keys():
                    # Increase the counter/value if the key is already in the dictionary
                    keys_values[key] += 1
                else:
                    # Add another key value pair to the dictionary if the pair does not already exist
                    keys_values.update({key: 1})

                # Sort the dictionary from greatest to least
                return dict(sorted(keys_values.items(), key=lambda count: count[1], reverse=True))

    def init_db(self) -> None:
        now = datetime.now()
        last_year = now.year - 1
        this_year = now.year
        next_year = now.year + 1

        self.collection.create()
        self.append_year(last_year)
        self.append_year(this_year)
        self.append_year(next_year)
        util.save_to_json(self.collection.all(), "cache_exported")

    def update(self, record) -> None:
        # Check cache if it has somewhere to store a new year
        this_year = self.year
        self.check_year(this_year)

        # Populate cache
        for year in self.collection:
            if year['year'] == this_year:
                # Counters
                if record['data_type'] == "alpr_group":
                    year['all_time_plates_captured'] += 1
                    year['month'][self.month - 1]['license_plates_captured'] += 1
                    # Objects
                    year['month'][self.month - 1]['camera'] = \
                        self.increase_dict_value_count("camera", record['web_server_config']['camera_label'])
                    year['month'][self.month - 1]['regions'] = \
                        self.increase_dict_value_count("regions", record['best_region'])
                elif record['data_type'] == "alpr_alert":
                    year['all_time_alerts'] += 1
                    year['month'][self.month - 1]['alerts'] += 1
                elif record['data_type'] == "vehicle":
                    year['all_time_vehicles'] += 1
                    year['month'][self.month - 1]['vehicles'] += 1

                self.collection.update(year['__id'], year)

        return
