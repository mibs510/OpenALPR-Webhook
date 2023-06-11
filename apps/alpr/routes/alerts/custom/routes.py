import logging

from flask import request, jsonify
from flask_login import current_user, login_required
import apps.helpers as helper

from apps import db
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.custom_alert import CustomAlert
from apps.alpr.routes.alerts.custom import blueprint
from apps.authentication.models import User, RoleType
from apps.helpers import message


@blueprint.route('/add', methods=["PUT"])
@login_required
def add():
    data = request.form

    alpr_group_id = data.get('alpr_group_id')
    license_plate = data.get('license_plate')
    region_match = bool(data.get('region_match'))
    description = data.get('description')
    username = current_user.username
    notify_user_ids = str(data.get('notify_user_ids')).split(',')

    user = User.find_by_username(username)

    if notify_user_ids != "null" and user.status != RoleType['ADMIN']:
        return jsonify({'error': message['illegal_access']}), 404

    custom_alert = CustomAlert.filter_by_license_plate(license_plate)
    if custom_alert is None or custom_alert.submitted_by_user_id != user.id:
        try:
            custom_alert = CustomAlert()
            custom_alert.alpr_group_id = alpr_group_id
            custom_alert.license_plate = license_plate
            custom_alert.region_match = region_match
            custom_alert.description = description
            custom_alert.notify_user_ids = notify_user_ids
            custom_alert.submitted_by_user_id = user.id
            custom_alert.save()
            return jsonify({'message': message['custom_alert_added_successfully']}), 200
        except Exception as ex:
            logging.exception(ex)
            return jsonify({'error': message['unknown_error_occurred']}), 404
    else:
        return jsonify({'error': message['duplicate_custom_alert']}), 404


@blueprint.route('/edit', methods=["PUT"])
@login_required
def edit():
    data = request.form

    id = int(data.get('id'))
    region_match = bool(data.get('region_match'))
    description = data.get('description')
    username = current_user.username
    notify_user_ids = data.get('notify_user_ids') if data.get('notify_user_ids') == 'null' else str(data.get('notify_user_ids')).split(',')

    user = User.find_by_username(username)

    if notify_user_ids != "null" and user.status != RoleType['ADMIN']:
        return jsonify({'error': message['illegal_access']}), 404

    custom_alert = CustomAlert.filter_by_id(id)
    if custom_alert:
        try:
            custom_alert.region_match = region_match
            custom_alert.description = description
            if notify_user_ids != 'null':
                custom_alert.notify_user_ids = notify_user_ids
            custom_alert.save()
            return jsonify({'message': message['custom_alert_updated_successfully']}), 200
        except Exception as ex:
            logging.exception(ex)
            return jsonify({'error': message['unknown_error_occurred']}), 404
    else:
        return jsonify({'error': message['unknown_error_occurred']}), 404


@blueprint.route('/query', methods=["GET"])
@login_required
def query():
    user = User.find_by_username(current_user.username)
    query = CustomAlert.query.order_by(CustomAlert.id.desc())
    query = query.filter_by(submitted_by_user_id=user.id)

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(CustomAlert.license_plate.like(f'%{search}%'), CustomAlert.description.like(f'%{search}%')))
    total = query.count()

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    dt = helper.Timezone(current_user)
    data = []
    for record in query:
        alpr_group = ALPRGroup.filter_by_id(record.alpr_group_id)
        data.append({
            'id': record.id,
            'site': alpr_group.web_server_config['agent_label'],
            'camera': alpr_group.web_server_config['camera_label'],
            'plate_number': record.license_plate,
            'plate_crop_jpeg': alpr_group.best_plate['plate_crop_jpeg'],
            'direction': alpr_group.travel_direction_class_tag,
            'confidence': alpr_group.best_confidence_percent,
            'time': dt.astimezone(alpr_group.epoch_start)
        })

    # response
    return {
        'data': data,
        'total': total,
    }


@blueprint.route('/<id>/choices.js', methods=["GET"])
@login_required
def setChoices(id):
    custom_alert = CustomAlert.filter_by_id(int(id))
    if custom_alert:
        return jsonify(helper.setChoices(current_user, custom_alert.notify_user_ids))
    else:
        return jsonify({'error': 'Custom alert not found'}), 404
