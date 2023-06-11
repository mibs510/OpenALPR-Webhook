from flask import request
from flask_login import current_user, login_required

from apps import db
from apps.alpr.models.alpr_alert import ALPRAlert
from apps.alpr.routes.alerts.rekor import blueprint
from apps import helpers as helper


@blueprint.route('/query', methods=["GET"])
@login_required
def query():
    query = ALPRAlert.query.order_by(ALPRAlert.id.desc())

    # search filter
    search = request.args.get('search')
    if search:
        query = query.filter(db.or_(ALPRAlert.plate_number.like(f'%{search}%'), ALPRAlert.site_name.like(f'%{search}%')))
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
            'site_name': record.site_name,
            'camera_name': record.camera_name,
            'plate_number': record.plate_number,
            'plate_crop_jpeg': record.group['best_plate']['plate_crop_jpeg'],
            'travel_direction_class_tag': record.travel_direction_class_tag,
            'best_confidence_percent': record.best_confidence_percent,
            'epoch_time': dt.astimezone(record.epoch_time)
        })

    # response
    return {
        'data': data,
        'total': total,
    }
