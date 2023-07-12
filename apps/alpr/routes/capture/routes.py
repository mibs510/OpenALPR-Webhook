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

import datetime

from flask import render_template
from flask_login import login_required, current_user

from apps import helpers
from apps.alpr.models.alpr_group import ALPRGroup
from apps.alpr.models.cache import CameraCache
from apps.alpr.models.settings import GeneralSettings
from apps.alpr.routes.capture import blueprint
from apps.authentication.models import UserProfile, User


@blueprint.route('/<id>', methods=["GET"])
@login_required
def plate(id):
    if id is None:
        return render_template('home/page-404.html')

    license_plate = ALPRGroup.filter_by_id_and_beautify(id)
    dt = helpers.Timezone(current_user)
    user_profile = UserProfile.find_by_user_id(current_user.id)

    if license_plate is None:
        return render_template('home/page-404.html')
    else:
        cached_camera = CameraCache.filter_by_id_and_beautify(license_plate['camera_id'])
        return render_template('home/capture.html', segment='search', license_plate=license_plate,
                               date=dt.astimezone(datetime.datetime.utcnow()),
                               user_profile=user_profile, cached_camera=cached_camera,
                               settings=GeneralSettings.get_settings(), users=User.get_list_of_users_w_user_profiles())


@blueprint.route('/print/<id>', methods=["GET"])
@login_required
def print_plate(id):
    if id is None:
        return render_template('home/page-404.html')

    license_plate = ALPRGroup.filter_by_id_and_beautify(id)
    dt = helpers.Timezone(current_user)

    if license_plate is None:
        return render_template('home/page-404.html')
    else:
        cached_camera = CameraCache.filter_by_id_and_beautify(license_plate['camera_id'])
        return render_template('home/capture-print.html', segment='search', license_plate=license_plate,
                               date=dt.astimezone(datetime.datetime.utcnow()),
                               user_profile=UserProfile.find_by_user_id(current_user.id), cached_camera=cached_camera,
                               settings=GeneralSettings.get_settings())
