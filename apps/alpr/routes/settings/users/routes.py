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

import logging

from flask import request, jsonify, render_template
from flask_login import login_required, current_user
from password_generator import PasswordGenerator

from apps import db, helpers
from apps.alpr.models.settings import EmailNotificationSettings
from apps.alpr.notify import Email, Tag
from apps.alpr.routes.settings.users import blueprint
from apps.authentication.models import User, UserProfile
from apps.authentication.routes import STATUS_ACTIVE, STATUS_SUSPENDED, ROLE_ADMIN, ROLE_USER
from apps.authentication.signals import user_saved_signals
from apps.authentication.util import hash_pass
from apps.helpers import message, password_validate, createAccessToken, get_ts


@blueprint.route('/check/smtp', methods=['POST'])
def check_smtp():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    settings = EmailNotificationSettings.get_settings()

    if settings is None:
        return jsonify({'error': 'Empty SMTP settings. Valid SMTP settings required to reset user passwords.'}), 404

    # Validate SMTP settings
    is_valid_hostname = helpers.is_valid_hostname(settings.hostname)
    is_valid_ip = helpers.is_valid_ip(settings.hostname)
    is_valid_port = helpers.is_valid_port(int(settings.port))
    is_valid_email = helpers.emailValidate(settings.username_email)
    are_valid_recipients = helpers.are_valid_email_recipients(settings.recipients)

    if not is_valid_hostname and not is_valid_ip:
        return jsonify({'error': message['ip_hostname_not_valid']}), 404
    if not is_valid_port:
        return jsonify({'error': message['port_not_valid']}), 404
    if not is_valid_email:
        return jsonify({'error': message['not_valid_smtp_username_email']}), 404
    if not are_valid_recipients:
        return jsonify({'error': message['not_valid_smtp_recipients']}), 404

    return jsonify({'message': ''}), 200


@blueprint.route('/edit', methods=['PUT'])
@login_required
def edit():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        data = request.form

        profile = UserProfile.find_by_id(data.get('user_id'))
        user = User.find_by_id(data.get('user_id'))

        if profile is not None and user is not None:

            # Check if we can modify admin status.
            desired_admin_status = data.get('administrator')
            if desired_admin_status == "on":
                desired_admin_status = ROLE_ADMIN
            elif desired_admin_status == None:
                desired_admin_status = ROLE_USER

            # Cannot demote super admin!
            if user.id == 1 and user.role != desired_admin_status:
                return jsonify({'error': message['access_denied']}), 404

            # Otherwise, change it!
            if user.role != desired_admin_status:
                if user.role == ROLE_ADMIN:
                    user.role = ROLE_USER
                else:
                    user.role = ROLE_ADMIN
                    # if check login failed
                    if user.failed_logins > 0:
                        user.failed_logins = 0

            # Check if we can suspend account
            desired_account_status = data.get('status')
            if desired_account_status == "on":
                desired_account_status = STATUS_ACTIVE
            elif desired_account_status == None:
                desired_account_status = STATUS_SUSPENDED

            # Cannot suspend super admin!
            if user.id == 1 and user.status != desired_account_status:
                return jsonify({'error': message['access_denied']}), 404

            if user.status != desired_account_status:
                if user.status == STATUS_ACTIVE:
                    user.status = STATUS_SUSPENDED
                else:
                    user.status = STATUS_ACTIVE
                    # if check login failed
                    if user.failed_logins > 0:
                        user.failed_logins = 0

            if data.get('email') != '':
                try:
                    profile.full_name = data.get('full_name')
                    profile.bio = data.get('bio')
                    profile.address = data.get('address')
                    profile.zipcode = data.get('zipcode')
                    profile.phone = data.get('phone')

                    # Check phone number validity
                    if data.get('phone') != "":
                        if not helpers.are_valid_sms_recipients(profile.phone):
                            return jsonify({'error': message['invalid_phone_number']}), 404

                    profile.email = data.get('email')
                    profile.website = data.get('website')

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

                # Check phone number validity
                if data.get('phone') != "":
                    if not helpers.are_valid_sms_recipients(profile.phone):
                        return jsonify({'error': message['invalid_phone_number']}), 404

                profile.website = data.get('website')

                profile.save()
                user.save()

        aMsg = message['user_updated_successfully']

        return jsonify({'message': aMsg}), 200

    else:
        return jsonify({'error': message['record_not_found']}), 404


@blueprint.route('/register', methods=['POST'])
def register():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    data = request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password != confirm_password:
        return jsonify({'error': message['pwd_not_match']}), 404

    # Check if username exists
    user = User.find_by_username(username)
    if user:
        return jsonify({'error': message['username_already_registered']}), 404

    # Check if email exists
    user = User.find_by_email(email)
    if user:
        return jsonify({'error': message['email_already_registered']}), 404

    valid_pwd = password_validate(password)
    if not valid_pwd:
        return jsonify({'error': valid_pwd}), 404

    user = User(**request.form)
    user.api_token = createAccessToken()
    user.api_token_ts = get_ts()
    user.save()

    # send signal for create profile
    user_saved_signals.send({"user_id": user.id, "email": user.email})

    return jsonify({'message': message['account_created_successfully']}), 200


@blueprint.route('/reset/password', methods=['POST'])
@login_required
def reset_password():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    data = request.form

    user_id = int(data.get('user_id'))
    user = User.find_by_id(user_id)

    if user is None:
        return jsonify({'error': 'User not found!'}), 404

    try:
        pg = PasswordGenerator()
        pg.minlen = 16
        pg.maxlen = 16
        pg.minuchars = 4
        pg.minlchars = 3
        pg.minnumbers = 4
        pg.minschars = 4
        password = pg.generate()
        user.password = hash_pass(password)
        email = Email()
        email.tag = Tag.ACCOUNT.value
        email.subject = "Password Reset"
        email.body = "Hello {},\nYour password has been reset.\nYour new password is: {}".format(user.username,
                                                                                                 password)
        email.recipients = [user.email]
        # Don't save the new user password unless an email was sent without an exception
        if email.send():
            user.save()
    except Exception as ex:
        logging.exception(ex)
        return jsonify({'error': 'Something went wrong! Please make sure email SMTP settings are correct.'}), 404

    return jsonify({'message': 'Password has been reset! User has been emailed with a new password.'}), 200


@blueprint.route("/search", methods=['GET'])
@login_required
def search():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'GET':
        query = User.query

        search = request.args.get('search')
        if search:
            query = query.filter(db.or_(User.username.like(f'%{search}%'), User.email.like(f'%{search}%'),
                                        User.api_token.like(f'%{search}%')))
        total = query.count()

        # pagination
        start = request.args.get('start', type=int, default=-1)
        length = request.args.get('length', type=int, default=-1)
        if start != -1 and length != -1:
            query = query.offset(start).limit(length)

        dt = helpers.Timezone(current_user)
        users_list = []
        for user in query:
            for profile in UserProfile.query.filter_by(user=user.id):
                users_data = {
                    'id': user.id,
                    'avatar': profile.image,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'status': user.status,
                    'date_created': dt.astimezone(user.date_created),
                    'full_name': profile.full_name,
                    'bio': profile.bio,
                    'address': profile.address,
                    'zipcode': profile.zipcode,
                    'phone': profile.phone,
                    'website': profile.website,
                    'image': profile.image,
                    'profile_id': profile.id,
                    'api_token': str(user.api_token[-4:]).upper()
                }
                users_list.append(users_data)

        return {
            'data': users_list,
            'total': total,
        }
