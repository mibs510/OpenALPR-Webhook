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

from flask import request, jsonify, render_template
from flask_login import current_user, login_required
import apps.helpers as helper

from apps import db, helpers
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
    notify_user_ids = [] if data.get('notify_user_ids') == 'null' else str(data.get('notify_user_ids')).split(',')


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


@blueprint.route('/delete/<int:id>', methods=["PUT"])
@login_required
def delete(id):

    alert_record = CustomAlert.filter_by_id(id)
    user = User.find_by_username(current_user.username)

    if alert_record:
        if user:
            if alert_record.submitted_by_user_id == user.id:
                alert_record.delete()
            else:
                return jsonify({'error': message['illegal_access']}), 404
        else:
            return jsonify({'error': message['user_not_found']}), 404
    else:
        return jsonify({'message': message['custom_alert_not_found']}), 200

    return jsonify({'message': message['custom_alert_added_successfully']}), 200


@blueprint.route('/edit', methods=["PUT"])
@login_required
def edit():
    data = request.form

    id = int(data.get('id'))
    custom_alert = CustomAlert.filter_by_id(id)
    region_match = bool(data.get('region_match'))
    description = data.get('description')
    username = current_user.username
    notify_user_ids = [] if data.get('notify_user_ids') == 'null' else str(data.get('notify_user_ids')).split(',')

    user = User.find_by_username(username)

    if notify_user_ids != "null" and user.role != RoleType['ADMIN']:
        return jsonify({'error': message['illegal_access']}), 404

    # Each user can only edit their own records
    if custom_alert:
        if custom_alert.submitted_by_user_id != user.id:
            return jsonify({'error': message['illegal_access']}), 404

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
            'plate_number': alpr_group.best_plate_number,
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
    if id is None:
        return render_template('home/page-404.html')

    custom_alert = CustomAlert.filter_by_id(int(id))
    if custom_alert:
        return jsonify(helper.setChoices(current_user, custom_alert.notify_user_ids))
    else:
        return jsonify({'error': 'Custom alert not found'}), 404
