from flask import render_template, request
from flask_login import login_required, current_user

from apps import db, helpers
from apps.alpr import beautify
from apps.alpr.models.alpr_alert import ALPRAlert
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.vehicle import Vehicle
from apps.alpr.routes.search import blueprint


@blueprint.route('/', methods=["GET"])
@login_required
def search():
    return render_template('home/search.html', segment='search')


@blueprint.route('/query/alert/<plate>', methods=["GET"])
@login_required
def query_alert_plate(plate):
    if plate is None:
        return render_template('home/page-404.html')

    query = ALPRAlert.query.filter_by(plate_number=plate).order_by(ALPRAlert.id.desc())
    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helpers.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'site': ALPRGroup.get_latest_agent_label(record.agent_uid),
            'camera': ALPRGroup.get_latest_camera_label(record.group['camera_id']),
            'plate_number': record.plate_number,
            'plate_crop_jpeg': record.group['best_plate']['plate_crop_jpeg'],
            'direction': record.travel_direction_class_tag,
            'confidence': record.best_confidence_percent,
            'time': dt.astimezone(record.epoch_time)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/query/group', methods=["GET"])
@login_required
def query_group():
    query = ALPRGroup.query.order_by(ALPRGroup.id.desc())

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(ALPRGroup.best_plate_number.like(f'%{search}%')))

    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helpers.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'site': record.web_server_config['agent_label'],
            'camera': record.web_server_config['camera_label'],
            'plate_number': record.best_plate_number,
            'plate_crop_jpeg': record.best_plate['plate_crop_jpeg'],
            'direction': record.travel_direction_class_tag,
            'confidence': record.best_confidence_percent,
            'time': dt.astimezone(record.epoch_start)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/query/<plate>', methods=["GET"])
@login_required
def query_plate(plate):
    if plate is None:
        return render_template('home/page-404.html')

    query = ALPRGroup.query.filter_by(best_plate_number=plate).order_by(ALPRGroup.id.desc())
    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helpers.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'site': record.web_server_config['agent_label'],
            'camera': record.web_server_config['camera_label'],
            'plate_number': record.best_plate_number,
            'plate_crop_jpeg': record.best_plate['plate_crop_jpeg'],
            'direction': record.travel_direction_class_tag,
            'confidence': record.best_confidence_percent,
            'time': dt.astimezone(record.epoch_start)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/query/vehicle', methods=["GET"])
@login_required
def query_vehicle():
    query = Vehicle.query.order_by(Vehicle.id.desc())

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(Vehicle.vehicle_color_name.like(f'%{search}%'),
                                    Vehicle.vehicle_make_name.like(f'%{search}%'),
                                    Vehicle.vehicle_make_model_name.like(f'%{search}%')))

    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helpers.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'site': ALPRGroup.get_latest_agent_label(record.agent_uid),
            'camera': ALPRGroup.get_latest_camera_label(record.camera_id),
            'color': beautify.name(record.vehicle_color_name),
            'ym': record.vehicle_year_name + " " + beautify.name(record.vehicle_make_model_name),
            'vehicle_crop_jpeg': record.vehicle_crop_jpeg,
            'direction': record.travel_direction_class_tag,
            'time': dt.astimezone(record.epoch_start)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/query/vehicle/signature/<signature>', methods=["GET"])
@login_required
def query_vehicle_signature(signature):
    if signature is None:
        return render_template('home/page-404.html')

    query = Vehicle.query.filter_by(vehicle_signature=signature).order_by(Vehicle.id.desc())

    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helpers.Timezone(current_user)
    data = []
    for record in query:
        data.append({
            'id': record.id,
            'site': ALPRGroup.get_latest_agent_label(record.agent_uid),
            'camera': ALPRGroup.get_latest_camera_label(record.camera_id),
            'color': beautify.name(record.vehicle_color_name),
            'ym': record.vehicle_year_name + " " + beautify.name(record.vehicle_make_model_name),
            'vehicle_crop_jpeg': record.vehicle_crop_jpeg,
            'direction': record.travel_direction_class_tag,
            'time': dt.astimezone(record.epoch_start)
        })

    # response
    return {
        'data': data,
        'total': total,
    }
