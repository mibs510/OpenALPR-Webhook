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

import pytz
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from flask_paginate import get_page_parameter, Pagination

from apps import ip_ban_config
from apps.alpr.models.settings import EmailNotificationSettings, TwilioNotificationSettings, GeneralSettings, PostAuth
from apps.alpr.routes.settings import blueprint
from apps.alpr.routes.settings.cameras.manufacturers import get_camera_manufacturers
from apps.authentication.models import User, UserProfile
from apps.authentication.routes import ROLE_ADMIN
from worker_manager import WorkerManager
from worker_manager_enums import WMSCommand


@blueprint.route('/agents', methods=["GET"])
@login_required
def agents():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    return render_template('settings/agents.html', segment='settings-agents')


@blueprint.route('/cameras', methods=["GET"])
@login_required
def cameras():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    return render_template('settings/cameras.html', segment='settings-camera', manufacturers=get_camera_manufacturers())


@blueprint.route('/general', methods=["GET"])
@login_required
def general():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    return render_template('settings/general.html', segment='settings-general', settings=GeneralSettings.get_settings(),
                           ipban=ip_ban_config.get_settings(), post_auth_levels=PostAuth)


@blueprint.route('/maintenance/app', methods=["GET"])
@login_required
def maintenance_app():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    wms_status = False
    try:
        wms = WorkerManager(WMSCommand.ACK)
        wms.send()
        wms_status = wms.last_connection()
    except Exception:
        pass

    return render_template('settings/maintenance-app.html', segment='settings-maintenance-app',
                           wms_status=wms_status)


@blueprint.route('/notifications', methods=["GET"])
@login_required
def notifications():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    smtp_settings = EmailNotificationSettings.get_settings()
    # Maybe it's a new instance of the app.
    if smtp_settings is None:
        smtp_settings = EmailNotificationSettings()
        smtp_settings.save()

    sms_settings = TwilioNotificationSettings.get_settings()
    # Maybe it's a new instance of the app.
    if sms_settings is None:
        sms_settings = TwilioNotificationSettings()
        sms_settings.save()

    return render_template('settings/notifications.html', segment='settings-notifications', smtp=smtp_settings,
                           sms=sms_settings)


@blueprint.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    """
        Get user profile view
    """
    if request.method == 'GET':
        template = 'settings/profile.html'

        user = User.find_by_id(current_user.id)
        user_profile = UserProfile.find_by_user_id(user.id)

        context = {'id': user.id,
                   'profile_name': user_profile.full_name,
                   'profile_bio': user_profile.bio,
                   'profile_address': user_profile.address,
                   'profile_zipcode': user_profile.zipcode,
                   'profile_phone': user_profile.phone,
                   'email': user_profile.email,
                   'profile_website': user_profile.website,
                   'profile_image': user_profile.image,
                   'user_profile_id': user_profile.id,
                   'api_token': user.api_token,
                   'profile_timezone': user_profile.timezone
                   }

        return render_template(template, context=context, segment='settings-profile', timezones=pytz.common_timezones)

    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/users', methods=['GET'])
@login_required
def users():
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for('home_blueprint.index'))

    if request.method == 'GET':
        template = '/settings/users.html'
        search = False
        q = request.args.get('q')
        if q:
            search = True

        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10

        # users records
        users_obj = User
        users = users_obj.query.paginate(page, per_page, error_out=True).items

        pagination = Pagination(page=page, per_page=per_page,
                                total=len(users_obj.query.all()), search=search, record_name='users')

        user_list = []
        if users is not None:
            for user in users:
                for data in UserProfile.query.filter_by(user=user.id):
                    user_list.append(data)

        return render_template(template,
                               users_data=user_list,
                               pagination=pagination,
                               segment='settings-users'
                               )

    return redirect(url_for('home_blueprint.index'))
