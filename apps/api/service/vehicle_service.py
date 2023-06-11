import datetime

from flask_restx import Resource
from apps.alpr.models.vehicle import Vehicle
import apps.alpr.beautify as beautify
from apps.messages import Messages

message = Messages.message


class VehicleService(Resource):
    def create(self, request_data: Vehicle):
        new_vehicle = Vehicle()

        new_vehicle.data_type = request_data.data_type
        new_vehicle.version = request_data.version
        new_vehicle.epoch_start = request_data.epoch_start
        new_vehicle.epoch_end = request_data.epoch_end
        new_vehicle.frame_start = request_data.frame_start
        new_vehicle.frame_end = request_data.frame_end
        new_vehicle.company_id = request_data.company_id
        new_vehicle.agent_uid = request_data.agent_uid
        new_vehicle.agent_version = request_data.agent_version
        new_vehicle.agent_type = request_data.agent_type
        new_vehicle.camera_id = request_data.camera_id
        new_vehicle.gps_latitude = request_data.gps_latitude
        new_vehicle.gps_longitude = request_data.gps_longitude
        new_vehicle.country = request_data.country
        new_vehicle.vehicle_crop_jpeg = request_data.vehicle_crop_jpeg
        new_vehicle.overview_jpeg = request_data.overview_jpeg
        new_vehicle.best_uuid = request_data.best_uuid
        new_vehicle.best_uuid_epoch_ms = request_data.best_uuid_epoch_ms
        new_vehicle.best_image_width = request_data.best_image_width
        new_vehicle.best_image_height = request_data.best_image_height
        new_vehicle.travel_direction = request_data.travel_direction
        new_vehicle.is_parked = request_data.is_parked
        new_vehicle.is_preview = request_data.is_preview
        new_vehicle.vehicle_signature = request_data.vehicle_signature
        new_vehicle.vehicle = request_data.vehicle
        new_vehicle.custom_data = request_data.custom_data

        # Custom
        new_vehicle.vehicle_color_name = beautify.name(request_data.vehicle['color'][0]['name'])
        new_vehicle.vehicle_color_confidence = beautify.round_percentage(
            request_data.vehicle['color'][0]['confidence'])
        new_vehicle.vehicle_make_name = beautify.name(request_data.vehicle['make'][0]['name'])
        new_vehicle.vehicle_make_confidence = beautify.round_percentage(request_data.vehicle['make'][0]['confidence'])
        new_vehicle.vehicle_make_model_name = beautify.name(request_data.vehicle['make_model'][0]['name'])
        new_vehicle.vehicle_make_model_confidence = beautify.round_percentage(
            request_data.vehicle['make_model'][0]['confidence'])
        new_vehicle.vehicle_body_type_name = beautify.name(request_data.vehicle['body_type'][0]['name'])
        new_vehicle.vehicle_body_type_confidence = beautify.round_percentage(
            request_data.vehicle['body_type'][0]['confidence'])
        new_vehicle.vehicle_year_name = request_data.vehicle['year'][0]['name']
        new_vehicle.vehicle_year_confidence = beautify.round_percentage(request_data.vehicle['year'][0]['confidence'])
        new_vehicle.vehicle_missing_plate_name = beautify.name(request_data.vehicle['missing_plate'][0]['name'])
        new_vehicle.vehicle_is_vehicle_name = beautify.name(request_data.vehicle['is_vehicle'][0]['name'])
        new_vehicle.vehicle_is_vehicle_confidence = beautify.round_percentage(
            request_data.vehicle['is_vehicle'][0]['confidence'])
        new_vehicle.travel_direction_class_tag = beautify.direction(request_data.travel_direction)

        new_vehicle.save()
        return new_vehicle
