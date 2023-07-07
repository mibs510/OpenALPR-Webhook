import logging
import platform

from flask import render_template, jsonify
from flask_login import login_required, current_user

import apps.alpr.get as Get
from apps.alpr.models.alpr_alert import ALPRAlert
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.cache import Cache, CameraCache, AgentCache
from apps.alpr.models.vehicle import Vehicle
from apps.alpr.routes.settings.maintenance import blueprint
from apps.api.schemas.alpr_alert_schema import ALPRAlertSchema
from apps.api.schemas.alpr_group_schema import ALPRGroupSchema
from apps.api.schemas.vehicle_schema import VehicleSchema
from apps.api.service.alpr_alert_service import ALPRAlertService
from apps.api.service.alpr_group_service import ALPRGroupService
from apps.api.service.vehicle_service import VehicleService
from apps.authentication.models import User
from apps.authentication.routes import ROLE_ADMIN
from worker_manager import WorkerManager
from worker_manager_enums import WMSCommand


@blueprint.route('/init/cache', methods=["GET"])
@login_required
def init_cache_db():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    # Drop all rows from each table
    Cache.query.delete()
    AgentCache.query.delete()
    CameraCache.query.delete()

    cache = Cache.filter_by_year()
    if cache is None:
        cache = Cache()
    cache.init()

    return jsonify({'msg': 'cache_initiated'}), 200


@blueprint.route('/import/db', methods=["GET"])
@login_required
def import_db():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    # Schemas
    alpr_alert_schema = ALPRAlertSchema()
    alpr_group_schema = ALPRGroupSchema()
    vehicle_schema = VehicleSchema()

    # Services
    alpr_alert_service = ALPRAlertService()
    alpr_group_service = ALPRGroupService()
    vehicle_service = VehicleService()

    get = Get.Get()
    group_collection = get.collection(database="group")
    logging.info("len(group_collection) = {}".format(len(group_collection)))
    alert_collection = get.collection(database="alert")
    logging.info("len(alert_collection) = {}".format(len(alert_collection)))
    vehicle_collection = get.collection(database="vehicle")
    logging.info("len(vehicle_collection) = {}".format(len(vehicle_collection)))

    for i in range(len(group_collection)):
        request_data = group_collection[i]
        try:
            validated_data = alpr_group_schema.load(request_data)
            alpr_group_service.create(validated_data)
        except Exception as ex:
            logging.debug("transfer_db: (alpr_group) ex = {}".format(ex))
            logging.debug("transfer_db: (alpr_group) request_data = {}".format(request_data))
    for i in range(len(alert_collection)):
        request_data = alert_collection[i]
        try:
            validated_data = alpr_alert_schema.load(request_data)
            alpr_alert_service.create(validated_data)
        except Exception as ex:
            logging.debug("transfer_db: (alpr_alert) ex = {}".format(ex))
            logging.debug("transfer_db: (alpr_alert) request_data = {}".format(request_data))
    for i in range(len(vehicle_collection)):
        request_data = vehicle_collection[i]
        try:
            validated_data = vehicle_schema.load(request_data)
            vehicle_service.create(validated_data)
        except Exception as ex:
            logging.debug("transfer_db: (vehicle) ex = {}".format(ex))
            logging.debug("transfer_db: (vehicle) request_data = {}".format(request_data))

    # Rewrite the API_TOKEN to that of the super_admin
    super_admin = User.find_by_id(1)
    if super_admin:
        alpr_group = ALPRGroup()
        alpr_alert = ALPRAlert()
        vehicle = Vehicle()

        for record in alpr_group.query:
            record.custom_data['API_KEY'] = super_admin.api_token
        for record in alpr_alert.query:
            record.custom_data['API_KEY'] = super_admin.api_token
        for record in vehicle.query:
            record.custom_data['API_KEY'] = super_admin.api_token

        alpr_group.save()
        alpr_alert.save()
        vehicle.save()

    return jsonify({'msg': "Records migrated to SQLite!"}), 200


@blueprint.route('/shutdown/wms', methods=["POST"])
@login_required
def shutdown_wms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if platform.system() != "Linux":
        return jsonify({'error': 'Unsupported platform. Redis server is not running.'}), 404

    try:
        wms = WorkerManager(WMSCommand.STOP_ALL)
        logging.debug("Sending STOP_ALL command")
        wms.send()
        wms.command = WMSCommand.STOP_SERVER
        logging.debug("Sending STOP_SERVER command")
        wms.send()
    except Exception or TimeoutError as ex:
        logging.exception(ex)
        return jsonify({'error': str(ex)}), 404

    return jsonify({'message': 'Worker Manager Server shutdown successfully!'}), 200


@blueprint.route('/restart/wms', methods=["GET"])
@login_required
def restart_wms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    try:

        wms = WorkerManager(WMSCommand.STOP_ALL)
        logging.debug("Sending STOP_ALL command")
        wms.send()
        wms.command = WMSCommand.STOP_SERVER
        logging.debug("Sending STOP_SERVER command")
        wms.send()

        from apps import start_redis_workers
        start_redis_workers()

    except Exception or TimeoutError as ex:
        logging.exception(ex)
        if TimeoutError:
            return jsonify({'error': 'Connection to Worker Manager Server timed out!'}), 404
        elif Exception:
            return jsonify({'error': 'Unknown error occurred!'}), 404

    return jsonify({'msg': 'Worker Manager Server shutdown successfully!'}), 200
