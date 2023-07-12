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
from apps.alpr.models.alpr_alert import ALPRAlert
from apps.alpr.models.cache import CameraCache, AgentCache
from apps.alpr.models.custom_alert import CustomAlert
from apps.alpr.models.settings import GeneralSettings
from apps.alpr.routes.alert import blueprint
from apps.authentication.models import UserProfile, User


@blueprint.route('/custom/<id>', methods=["GET"])
@login_required
def custom_alert(id):
    if id is None:
        return render_template('home/page-404.html')

    alert = CustomAlert.filter_by_id_and_beautify(id)
    dt = helpers.Timezone(current_user)

    if alert is None:
        return render_template('home/page-404.html')
    else:
        cached_agent = AgentCache.filter_by_agent_uid(alert['agent_uid'])
        cached_camera = CameraCache.filter_by_id_and_beautify(alert['camera_id'])
        return render_template('home/custom-alert.html', segment='alerts-custom-alert', alert=alert,
                               date=dt.astimezone(datetime.datetime.utcnow()),
                               user_profile=UserProfile.find_by_user_id(current_user.id), cached_agent=cached_agent,
                               cached_camera=cached_camera, settings=GeneralSettings.get_settings(),
                               users=User.get_list_of_users_w_user_profiles())


@blueprint.route('/custom/print/<id>', methods=["GET"])
@login_required
def print_custom_alert(id):
    if id is None:
        return render_template('home/page-404.html')

    alert = ALPRAlert.filter_by_id_and_beautify(id)
    dt = helpers.Timezone(current_user)

    if alert is None:
        return render_template('home/page-404.html')
    else:
        cached_agent = AgentCache.filter_by_agent_uid(alert['agent_uid'])
        cached_camera = CameraCache.filter_by_id_and_beautify(alert['camera_id'])
        return render_template('home/custom-alert.html', segment='alerts-custom-print-alert', alert=alert,
                               date=dt.astimezone(datetime.datetime.utcnow()),
                               user_profile=UserProfile.find_by_user_id(current_user.id), cached_agent=cached_agent,
                               cached_camera=cached_camera, settings=GeneralSettings.get_settings())


@blueprint.route('/rekor/<id>', methods=["GET"])
@login_required
def alpr_alert(id):
    if id is None:
        return render_template('home/page-404.html')

    alert = ALPRAlert.filter_by_id_and_beautify(id)
    dt = helpers.Timezone(current_user)

    if alert is None:
        return render_template('home/page-404.html')
    else:
        cached_agent = AgentCache.filter_by_agent_uid(alert['agent_uid'])
        cached_camera = CameraCache.filter_by_id_and_beautify(alert['camera_id'])
        return render_template('home/alert.html', segment='alerts-rekor-alert', alert=alert,
                               date=dt.astimezone(datetime.datetime.utcnow()),
                               user_profile=UserProfile.find_by_user_id(current_user.id), cached_agent=cached_agent,
                               cached_camera=cached_camera, settings=GeneralSettings.get_settings())


@blueprint.route('/rekor/print/<id>', methods=["GET"])
@login_required
def print_alpr_alert(id):
    if id is None:
        return render_template('home/page-404.html')

    alert = ALPRAlert.filter_by_id_and_beautify(id)
    dt = helpers.Timezone(current_user)

    if alert is None:
        return render_template('home/page-404.html')
    else:
        cached_agent = AgentCache.filter_by_agent_uid(alert['agent_uid'])
        cached_camera = CameraCache.filter_by_id_and_beautify(alert['camera_id'])
        return render_template('home/alert-print.html', segment='alerts-rekor-print-alert', alert=alert,
                               date=dt.astimezone(datetime.datetime.utcnow()),
                               user_profile=UserProfile.find_by_user_id(current_user.id), cached_agent=cached_agent,
                               cached_camera=cached_camera, settings=GeneralSettings.get_settings())
