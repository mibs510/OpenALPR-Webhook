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
