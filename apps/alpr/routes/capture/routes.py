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
