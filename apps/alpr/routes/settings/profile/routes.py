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

from flask import request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from apps import helpers
from apps.alpr.routes.settings.profile import blueprint
from apps.authentication.models import User, UserProfile
from apps.authentication.routes import upload_folder_name, ROLE_ADMIN, ROLE_USER, STATUS_ACTIVE, STATUS_SUSPENDED
from apps.authentication.util import hash_pass
from apps.helpers import message, unique_file_name, password_validate, are_valid_sms_recipients


@blueprint.route('/edit', methods=['GET', 'PUT'])
@login_required
def edit():
    """
        1.Get User by id(Get user view)
        2.Update user(update user view)
    Returns:
        _type_: json data
    """
    if request.method == 'GET':

        profile = UserProfile.find_by_id(request.args.get('user_id'))
        user = User.find_by_id(request.args.get('user_id'))

        # if check user none or not
        if profile and user:

            context = {'id': profile.id, 'full_name': profile.full_name, 'bio': profile.bio,
                       'address': profile.address, 'zipcode': profile.zipcode, 'phone': profile.phone,
                       'email': profile.email, 'website': profile.website, 'image': profile.image,
                       'user_id': profile.user_id.id, 'api_key': str(user.api_token).upper(), 'status': user.status,
                       'administrator': user.role, 'timezone': profile.timezone}

            return jsonify(context), 200

        else:
            return jsonify({'error': message['record_not_found']}), 404

    if request.method == 'PUT':
        data = request.form
        image = request.files.get('image')

        profile = UserProfile.find_by_id(data.get('user_id'))
        user = User.find_by_id(data.get('user_id'))

        if profile is not None and user is not None:
            # Form data checks
            if not are_valid_sms_recipients(data.get('phone')):
                return jsonify({'error': message['invalid_phone_number']}), 404

            # Change avatar
            if image:
                # Create directory if it doesn't exist
                helpers.mkdir(upload_folder_name)
                filename = unique_file_name(secure_filename(image.filename))
                full_file_path = os.path.join(upload_folder_name, filename)
                try:
                    image.save(full_file_path)
                    with open(full_file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    profile.image = encoded_string.decode("utf-8")
                    user.avatar = encoded_string.decode("utf-8")
                    if os.path.isfile(full_file_path):
                        os.remove(full_file_path)
                except Exception as ex:
                    if os.path.isfile(full_file_path):
                        os.remove(full_file_path)
                    logging.exception(ex)
                    return jsonify({'error': message['error_updating_user_profile']}), 500

            if data.get('email') != '':
                try:
                    profile.full_name = data.get('full_name')
                    profile.bio = data.get('bio')
                    profile.address = data.get('address')
                    profile.zipcode = data.get('zipcode')
                    profile.phone = data.get('phone')
                    profile.email = data.get('email')
                    profile.website = data.get('website')
                    profile.timezone = data.get('timezone')

                    profile.save()
                    user.save()
                except:
                    return jsonify({'error': "Email already exists."}), 404

                profile = User.find_by_id(data.get('user_id'))
                profile.email = data.get('email')
                profile.save()
            else:
                profile.full_name = data.get('full_name')
                profile.bio = data.get('bio')
                profile.address = data.get('address')
                profile.zipcode = data.get('zipcode')
                profile.phone = data.get('phone')
                profile.website = data.get('website')
                profile.timezone = data.get('timezone')

                profile.save()
                user.save()

        aMsg = message['user_updated_successfully']

        return jsonify({'message': aMsg}), 200

    else:
        return jsonify({'error': message['record_not_found']}), 404


@blueprint.route('/update/password', methods=['POST'])
@login_required
def update_password():
    """Change an existing user's password."""
    data = request.form
    new_password = data.get('new_password')
    new_password2 = data.get('new_password2')

    user = User.find_by_username(current_user.username)

    if request.method == 'POST':
        # password validate
        valid_pwd = password_validate(new_password)
        if valid_pwd != True:
            return jsonify({'error': valid_pwd}), 404

        # check password match or not
        if new_password != new_password2:
            return jsonify({'error': message['pwd_not_match']}), 404

        # if check old password none
        else:
            user.password = hash_pass(new_password)
            user.save()

        return jsonify({'message': message['password_has_been_updated']}), 200
