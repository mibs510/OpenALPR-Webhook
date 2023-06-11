from flask import render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func

from apps import db, helpers
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.routes.search import blueprint


@blueprint.route('/', methods=["GET"])
@login_required
def search():
    return render_template('home/search.html', segment='search')


@blueprint.route('/query', methods=["GET"])
@login_required
def query():
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


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
