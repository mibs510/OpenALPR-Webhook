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
