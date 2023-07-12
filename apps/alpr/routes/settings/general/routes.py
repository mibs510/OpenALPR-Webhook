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

import base64
import logging
import os

from flask import request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from apps import ip_ban_config
from apps.alpr.models.settings import GeneralSettings, default_org_logo, PostAuth
from apps.alpr.routes.settings.general import blueprint
from apps.authentication.routes import upload_folder_name, ROLE_ADMIN
from apps.helpers import unique_file_name, message


@blueprint.route('/edit/general', methods=['POST'])
@login_required
def edit_general_settings():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'POST':
        data = request.form
        settings = GeneralSettings.get_settings()

        # Create a row of settings in case they weren't initialized previously on start up
        if settings is None:
            settings = GeneralSettings()

        if settings:
            settings.public_url = data.get('public_url')
            settings.save()

            return jsonify({'message': message['general_settings_saved']}), 200
        else:
            return jsonify({'error': message['general_settings_not_saved']}), 404


@blueprint.route('/edit/ipban', methods=['POST'])
@login_required
def edit_ipban_settings():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'POST':
        data = request.form

        settings = ip_ban_config

        if settings:
            ipban_ban_count = int(data.get('ipban_ban_count'))
            ipban_ban_seconds = int(data.get('ipban_ban_seconds'))
            ipban_persist = bool(data.get('ipban_persist'))
            ipban_ip_header = data.get('ipban_ip_header')
            ipban_abuse_IPDB_config_report = bool(data.get('ipban_abuse_IPDB_config_report'))
            ipban_abuse_IPDB_config_load = bool(data.get('ipban_abuse_IPDB_config_load'))
            ipban_abuse_IPDB_config_key = data.get('ipban_abuse_IPDB_config_key')

            if ipban_ban_count <= 0:
                return jsonify({'error': message['ipban_invalid_ban_count']}), 404
            if ipban_ban_seconds < 0:
                return jsonify({'error': message['ipban_invalid_ban_seconds']}), 404
            if ipban_abuse_IPDB_config_report or ipban_abuse_IPDB_config_load:
                if ipban_abuse_IPDB_config_key == "":
                    return jsonify({'error': message['ipban_key_needed_to_report_load']}), 404

            settings.ban_count = str(ipban_ban_count)
            settings.ban_seconds = str(ipban_ban_seconds)
            settings.persist = str(ipban_persist)
            settings.ip_header = str(ipban_ip_header)
            settings.abuse_IPDB_config_report = str(ipban_abuse_IPDB_config_report)
            settings.abuse_IPDB_config_load = str(ipban_abuse_IPDB_config_load)
            settings.abuse_IPDB_config_key = ipban_abuse_IPDB_config_key

            settings.save()

            return jsonify({'message': message['ipban_settings_saved']}), 200
        else:
            return jsonify({'error': message['ipban_settings_not_saved']}), 404


@blueprint.route('/edit/report', methods=['POST'])
@login_required
def edit_report_settings():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'POST':
        data = request.form
        logo = request.files.get('org_logo')

        settings = GeneralSettings.get_settings()

        # Create a row of settings in case they weren't initialized previously on start up
        if settings is None:
            settings = GeneralSettings()

        if settings:
            # Change organization logo
            if logo:
                filename = unique_file_name(secure_filename(logo.filename))
                full_file_path = os.path.join(upload_folder_name, filename)
                try:
                    logo.save(full_file_path)
                    with open(full_file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    settings.logo = encoded_string.decode("utf-8")
                    if os.path.isfile(full_file_path):
                        os.remove(full_file_path)
                except Exception as ex:
                    if os.path.isfile(full_file_path):
                        os.remove(full_file_path)
                    logging.exception(ex)
                    return jsonify({'error': message['error_updating_brand_logo']}), 500

            # Organization name
            settings.org_name = data.get('org_name')
            settings.save()

            return jsonify({'message': message['report_settings_saved']}), 200
        else:
            return jsonify({'error': message['report_settings_not_saved']}), 404


@blueprint.route('/reset/report', methods=['POST'])
@login_required
def reset_report_settings():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'POST':
        settings = GeneralSettings.get_settings()

        # Create a row of settings in case they weren't initialized previously on start up
        if settings is None:
            settings = GeneralSettings()

        if settings:
            # Reset brand settings to default
            settings.org_name = "OpenALPR-Webhook"
            settings.logo = default_org_logo
            settings.save()

            return jsonify({'message': message['report_settings_saved']}), 200
        else:
            return jsonify({'error': message['report_settings_not_saved']}), 404


@blueprint.route('/edit/post_auth', methods=['POST'])
@login_required
def edit_post_auth_settings():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'POST':
        data = request.form
        settings = GeneralSettings.get_settings()

        # Create a row of settings in case they weren't initialized previously on start up
        if settings is None:
            settings = GeneralSettings()

        if settings:
            settings.post_auth = PostAuth(int(data.get('post_auth')))
            settings.save()

            return jsonify({'message': message['post_auth_settings_saved']}), 200
        else:
            return jsonify({'error': message['post_auth_settings_not_saved']}), 404
