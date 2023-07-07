import logging
import time

from flask import render_template, request, jsonify
from flask_login import current_user, login_required
from redis.client import Redis
from rq import Queue

from apps import db
from apps.alpr import queue
from apps.alpr.models.cache import CameraCache
from apps.alpr.models.settings import CameraSettings
from apps.alpr.routes.settings.cameras import blueprint
from apps.alpr.routes.settings.cameras.manufacturers.Dahua import Dahua
from apps.authentication.routes import ROLE_ADMIN
from apps.helpers import message
import apps.helpers as helper
from worker_manager import WorkerManager
from worker_manager_enums import WMSCommand, WorkerType


@blueprint.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'GET':
        camera = CameraSettings.filter_by_id(request.args.get('id'))
        cache = CameraCache.filter_by_camera_id(camera.camera_id)

        if cache is None:
            gps_latitude = -1
            gps_longitude = -1
        else:
            gps_latitude = cache.gps_latitude
            gps_longitude = cache.gps_longitude

        dt = helper.Timezone(current_user)

        if camera:
            context = {'id': camera.id, 'camera_id': camera.camera_id, 'camera_label': camera.camera_label,
                       'hostname': camera.hostname, 'port': camera.port, 'username': camera.username,
                       'password': camera.password, 'focus': camera.focus, 'zoom': camera.zoom,
                       'focus_zoom_interval_check': camera.focus_zoom_interval_check,
                       'notify_on_failed_interval_check': camera.notify_on_failed_interval_check,
                       'manufacturer': camera.manufacturer, 'enable': camera.enable,
                       'created': dt.astimezone(camera.created), 'last_seen': dt.astimezone(camera.last_seen),
                       'gps_latitude': gps_latitude, 'gps_longitude': gps_longitude
                       }
            return jsonify(context), 200
        else:
            return jsonify({'error': message['record_not_found']}), 404

    if request.method == 'POST':
        return_save = save()
        if return_save == "ip_hostname_not_valid":
            return jsonify({'error': message['ip_hostname_not_valid']}), 404
        elif return_save == "port_not_valid":
            return jsonify({'error': message['port_not_valid']}), 404
        elif return_save == "ip_hostname_not_valid":
            return jsonify({'error': message['ip_hostname_not_valid']}), 404
        elif return_save == "port_not_valid":
            return jsonify({'error': message['port_not_valid']}), 404
        elif return_save == "could_not_process":
            return jsonify({'error': message['could_not_process']}), 404
        elif return_save == "camera_updated":
            return jsonify({'message': message['camera_updated']}), 200
        elif return_save == "camera_not_found":
            return jsonify({'error': message['camera_not_found']}), 404


@blueprint.route('/get/focus_zoom', methods=['POST'])
@login_required
def get_focus_zoom():
    return_save = save()
    if return_save == "ip_hostname_not_valid":
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    elif return_save == "port_not_valid":
        return jsonify({'error': message['port_not_valid']}), 404
    elif return_save == "ip_hostname_not_valid":
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    elif return_save == "port_not_valid":
        return jsonify({'error': message['port_not_valid']}), 404
    elif return_save == "could_not_process":
        return jsonify({'error': message['could_not_process']}), 404
    elif return_save == "camera_not_found":
        return jsonify({'error': message['camera_not_found']}), 404
    elif return_save == "camera_updated":
        data = request.form
        # Lets find the camera in the db
        camera = CameraSettings.filter_by_id(data.get('id'))

        if camera.manufacturer == "Dahua":
            camif = Dahua(camera.camera_label, camera.camera_id, camera.username, camera.password, camera.hostname,
                          str(camera.port), camera.focus, camera.zoom)
            try:
                focus_zoom_values = camif.get_focus_zoom_values()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['camera_get_focus_zoom_issue']}), 404
        else:
            return jsonify({'error': message['camera_unknown_manufacturer']}), 404

        return jsonify({'message': focus_zoom_values}), 200


def save():
    data = request.form

    # Validate before proceeding
    hostname = data.get('hostname')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    focus = data.get('focus')
    zoom = data.get('zoom')
    focus_zoom_interval_check = data.get('focus_zoom_interval_check')
    notify_on_failed_interval_check = bool(data.get('notify_on_failed_interval_check'))
    manufacturer = data.get('manufacturer')
    enable = bool(data.get('enable'))

    # Check to if we can even put the values through the validators
    if len(hostname) == 0:
        return "ip_hostname_not_valid"
    if port is None:
        return "port_not_valid"
    else:
        # Cast it as an int
        port = int(port)

    is_valid_hostname = helper.is_valid_hostname(hostname)
    is_valid_ip = helper.is_valid_ip(hostname)

    if not is_valid_hostname and not is_valid_ip:
        return "ip_hostname_not_valid"
    if not helper.is_valid_port(port):
        return "port_not_valid"

    # Lets find the agent in the db
    camera = CameraSettings.filter_by_id(data.get('id'))

    if camera:
        try:
            # Update it!
            camera.hostname = hostname
            camera.port = port
            camera.username = username
            camera.password = password
            camera.focus = focus
            camera.zoom = zoom
            camera.focus_zoom_interval_check = focus_zoom_interval_check
            camera.notify_on_failed_interval_check = notify_on_failed_interval_check
            camera.manufacturer = manufacturer
            previously_enabled = camera.enable
            camera.enable = enable
            camera.save()
            try:
                if previously_enabled != enable:
                    if enable:
                        wms = WorkerManager(WMSCommand.START_WORKER)
                        wms.debug = True
                        wms.worker_type = WorkerType.Camera
                        wms.worker_id = camera.camera_id
                        wms.send()
                        time.sleep(1)
                        # Add the function to the queue
                        q = Queue(camera.camera_id, connection=Redis())
                        q.enqueue(queue.focus_camera, args=(camera.camera_id,), job_timeout=-1)
                    else:
                        wms = WorkerManager(WMSCommand.STOP_WORKER)
                        wms.debug = True
                        wms.worker_id = camera.camera_id
                        wms.send()
            except Exception as ex:
                logging.exception(ex)
        except Exception as ex:
            logging.exception(ex)
            return "could_not_process"

        return "camera_updated"
    else:
        return "camera_not_found"


@blueprint.route('/search', methods=["GET"])
@login_required
def search():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    query = CameraSettings.query

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(CameraSettings.camera_id.like(f'%{search}%'), CameraSettings.camera_label.like(f'%{search}%')))
    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helper.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'camera_id': record.camera_id,
            'camera_label': record.camera_label,
            'hostname': record.hostname,
            'port': record.port,
            'focus': record.focus,
            'zoom': record.zoom,
            'focus_zoom_interval_check': record.focus_zoom_interval_check,
            'last_seen': dt.astimezone(record.last_seen)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/set/focus_zoom', methods=['POST'])
@login_required
def set_focus_zoom():
    return_save = save()
    if return_save == "ip_hostname_not_valid":
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    elif return_save == "port_not_valid":
        return jsonify({'error': message['port_not_valid']}), 404
    elif return_save == "ip_hostname_not_valid":
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    elif return_save == "port_not_valid":
        return jsonify({'error': message['port_not_valid']}), 404
    elif return_save == "could_not_process":
        return jsonify({'error': message['could_not_process']}), 404
    elif return_save == "camera_not_found":
        return jsonify({'error': message['camera_not_found']}), 404
    elif return_save == "camera_updated":
        data = request.form
        # Lets find the camera in the db
        camera = CameraSettings.filter_by_id(data.get('id'))

        if camera.manufacturer == "Dahua":
            camif = Dahua(camera.camera_label, camera.camera_id, camera.username, camera.password, camera.hostname,
                          str(camera.port), camera.focus, camera.zoom)
            try:
                focus_zoom_status = camif.set_focus_and_zoom()
            except Exception:
                return jsonify({'error': message['camera_set_focus_zoom_issue']}), 404
        else:
            return jsonify({'error': message['camera_unknown_manufacturer']}), 404

        if focus_zoom_status:
            return jsonify({'message': message['camera_set_focus_zoom']}), 200
        else:
            return jsonify({'error': message['camera_set_focus_zoom_failed']}), 404


@blueprint.route('/auto_focus', methods=['POST'])
@login_required
def auto_focus():
    return_save = save()
    if return_save == "ip_hostname_not_valid":
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    elif return_save == "port_not_valid":
        return jsonify({'error': message['port_not_valid']}), 404
    elif return_save == "ip_hostname_not_valid":
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    elif return_save == "port_not_valid":
        return jsonify({'error': message['port_not_valid']}), 404
    elif return_save == "could_not_process":
        return jsonify({'error': message['could_not_process']}), 404
    elif return_save == "camera_not_found":
        return jsonify({'error': message['camera_not_found']}), 404
    elif return_save == "camera_updated":
        data = request.form
        # Lets find the camera in the db
        camera = CameraSettings.filter_by_id(data.get('id'))

        if camera.manufacturer == "Dahua":
            camif = Dahua(camera.camera_label, camera.camera_id, camera.username, camera.password, camera.hostname,
                          str(camera.port), camera.focus, camera.zoom)
            try:
                auto_focus_zoom_status = camif.auto_focus()
            except Exception:
                return jsonify({'error': message['camera_auto_focus_issue']}), 404
        else:
            return jsonify({'error': message['camera_unknown_manufacturer']}), 404

        if auto_focus_zoom_status:
            return jsonify({'message': message['camera_auto_focus']}), 200
        else:
            return jsonify({'error': message['camera_auto_focus_failed']}), 404
