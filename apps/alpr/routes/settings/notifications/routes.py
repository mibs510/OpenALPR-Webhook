import logging

from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from apps.alpr.models.settings import EmailNotificationSettings, TwilioNotificationSettings
from apps.alpr.notify import Email, SMS
from apps.alpr.routes.settings.notifications import blueprint
from apps.authentication.routes import ROLE_ADMIN
from apps.helpers import message
import apps.helpers as helper


@blueprint.route('/edit/smtp', methods=['PUT'])
@login_required
def edit_smtp():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        data = request.form

        # Validate before proceeding
        hostname = data.get('smtp_hostname')
        port = data.get('smtp_port')
        username_email = data.get('smtp_username_email')
        password = data.get('smtp_password')
        recipients = data.get('smtp_recipients')

        # Check to if we can even put the values through the validators
        if len(hostname) == 0:
            return jsonify({'error': message['ip_hostname_not_valid']}), 404

        is_valid_hostname = helper.is_valid_hostname(hostname)
        is_valid_ip = helper.is_valid_ip(hostname)
        is_valid_port = helper.is_valid_port(int(port))
        is_valid_email = helper.emailValidate(username_email)
        are_valid_recipients = helper.are_valid_email_recipients(recipients)

        if not is_valid_hostname and not is_valid_ip:
            return jsonify({'error': message['ip_hostname_not_valid']}), 404
        if not is_valid_port:
            return jsonify({'error': message['port_not_valid']}), 404
        if not is_valid_email:
            return jsonify({'error': message['not_valid_smtp_username_email']}), 404
        if not are_valid_recipients:
            return jsonify({'error': message['not_valid_smtp_recipients']}), 404

        # Lets find the settings in the db
        email_notification_settings = EmailNotificationSettings.get_settings()

        if email_notification_settings:
            try:
                # Update it!
                email_notification_settings.hostname = hostname
                email_notification_settings.port = port
                email_notification_settings.username_email = username_email
                email_notification_settings.password = password
                email_notification_settings.recipients = recipients
                email_notification_settings.save()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404
            return jsonify({'message': message['smtp_updated']}), 200
        else:
            return jsonify({'error': message['smtp_settings_not_found']}), 404


@blueprint.route('/enable/smtp', methods=['PUT'])
@login_required
def enable_smtp():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        # Lets find the settings in the db
        email_notification_settings = EmailNotificationSettings.get_settings()

        if email_notification_settings:
            email_notification_settings.enabled = True
            try:
                email_notification_settings.save()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404
            return jsonify({'message': message['smtp_updated']}), 200
        else:
            return jsonify({'error': message['smtp_settings_not_found']}), 404


@blueprint.route('/disable/smtp', methods=['PUT'])
@login_required
def disable_smtp():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        # Lets find the settings in the db
        email_notification_settings = EmailNotificationSettings.get_settings()

        if email_notification_settings:
            email_notification_settings.enabled = False
            try:
                email_notification_settings.save()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404
            return jsonify({'message': message['smtp_updated']}), 200
        else:
            return jsonify({'error': message['smtp_settings_not_found']}), 404


@blueprint.route('/test/smtp', methods=['PUT'])
@login_required
def test_smtp():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        # Lets find the settings in the db
        email_notification_settings = EmailNotificationSettings.get_settings()

        if email_notification_settings:
            # Validate before proceeding
            hostname = email_notification_settings.hostname
            port = email_notification_settings.port
            username_email = email_notification_settings.username_email
            password = email_notification_settings.password
            recipients = email_notification_settings.recipients

            # Check to if we can even put the values through the validators
            if len(hostname) == 0:
                return jsonify({'error': message['ip_hostname_not_valid']}), 404

            is_valid_hostname = helper.is_valid_hostname(hostname)
            is_valid_ip = helper.is_valid_ip(hostname)
            is_valid_port = helper.is_valid_port(port)
            is_valid_email = helper.emailValidate(username_email)
            are_valid_recipients = helper.are_valid_email_recipients(recipients)

            if not is_valid_hostname and not is_valid_ip:
                return jsonify({'error': message['ip_hostname_not_valid']}), 404
            if not is_valid_port:
                return jsonify({'error': message['port_not_valid']}), 404
            if not is_valid_email:
                return jsonify({'error': message['not_valid_smtp_username_email']}), 404
            if not are_valid_recipients:
                return jsonify({'error': message['not_valid_smtp_recipients']}), 404

            try:
                email = Email()
                email.send_test()
            except Exception as ex:
                logging.exception(ex)
                # [WinError 10061] No connection could be made because the target machine actively refused it ->
                # ['[WinError 10061', ' No connection could be made because the target machine actively refused it']
                ex = str(ex).split(']')
                return jsonify({'error': message['smtp_test_unsuccessful'] + ex[1]}), 404
            # Success!
            return jsonify({'message': message['smtp_test_successful']}), 200
        else:
            return jsonify({'error': message['smtp_settings_not_found']}), 404


@blueprint.route('/enable/sms', methods=['PUT'])
@login_required
def enable_sms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        # Lets find the settings in the db
        sms_notification_settings = TwilioNotificationSettings.get_settings()

        if sms_notification_settings:
            sms_notification_settings.enabled = True
            try:
                sms_notification_settings.save()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404
            return jsonify({'message': message['sms_updated']}), 200
        else:
            return jsonify({'error': message['sms_settings_not_found']}), 404


@blueprint.route('/disable/sms', methods=['PUT'])
@login_required
def disable_sms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        # Lets find the settings in the db
        sms_notification_settings = TwilioNotificationSettings.get_settings()

        if sms_notification_settings:
            sms_notification_settings.enabled = False
            try:
                sms_notification_settings.save()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404
            return jsonify({'message': message['sms_updated']}), 200
        else:
            return jsonify({'error': message['sms_settings_not_found']}), 404


@blueprint.route('/edit/sms', methods=['PUT'])
@login_required
def edit_sms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        data = request.form

        # Validate before proceeding
        account_sid = data.get('sms_account_sid')
        auth_token = data.get('sms_auth_token')
        phone_number = data.get('sms_phone_number')
        recipients = data.get('sms_recipients')

        is_valid_phone_number = helper.are_valid_sms_recipients(phone_number)
        are_valid_recipients = helper.are_valid_sms_recipients(recipients)

        if len(account_sid) != 34:
            return jsonify({'error': message['sms_invalid_account_sid']}), 404
        if len(auth_token) != 32:
            return jsonify({'error': message['sms_invalid_auth_token']}), 404
        if not is_valid_phone_number:
            return jsonify({'error': message['sms_invalid_phone_number']}), 404
        if not are_valid_recipients:
            return jsonify({'error': message['sms_invalid_recipients']}), 404

        # Let's find the settings in the db
        sms_notification_settings = TwilioNotificationSettings.get_settings()

        if sms_notification_settings:
            try:
                # Update it!
                sms_notification_settings.account_sid = account_sid
                sms_notification_settings.auth_token = auth_token
                sms_notification_settings.phone_number = phone_number
                sms_notification_settings.recipients = recipients
                sms_notification_settings.save()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['could_not_process']}), 404
            return jsonify({'message': message['sms_updated']}), 200
        else:
            return jsonify({'error': message['sms_settings_not_found']}), 404


@blueprint.route('/test/sms', methods=['PUT'])
@login_required
def test_sms():
    if current_user.role != ROLE_ADMIN:
        return render_template('home/page-403.html')

    if request.method == 'PUT':
        # Lets find the settings in the db
        sms_notification_settings = TwilioNotificationSettings.get_settings()

        if sms_notification_settings:
            # Validate before proceeding
            account_sid = sms_notification_settings.account_sid
            auth_token = sms_notification_settings.auth_token
            phone_number = sms_notification_settings.phone_number
            recipients = sms_notification_settings.recipients

            is_valid_phone_number = helper.are_valid_sms_recipients(phone_number)
            are_valid_recipients = helper.are_valid_sms_recipients(recipients)

            if len(account_sid) != 34:
                return jsonify({'error': message['sms_invalid_account_sid']}), 404
            if len(auth_token) != 32:
                return jsonify({'error': message['sms_invalid_auth_token']}), 404
            if not is_valid_phone_number:
                return jsonify({'error': message['sms_invalid_phone_number']}), 404
            if not are_valid_recipients:
                return jsonify({'error': message['sms_invalid_recipients']}), 404

            try:
                sms = SMS()
                sms.send_test()
            except Exception as ex:
                logging.exception(ex)
                return jsonify({'error': message['sms_test_unsuccessful']}), 404

            # Success!
            return jsonify({'message': message['sms_test_successful']}), 200
        else:
            return jsonify({'error': message['sms_settings_not_found']}), 404
