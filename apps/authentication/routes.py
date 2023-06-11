from flask import Flask
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user, login_required, AnonymousUserMixin
)


from apps import login_manager
from apps import ip_ban
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import User
from apps.authentication.signals import user_saved_signals
from apps.authentication.util import verify_pass
from apps.config import Config
from apps.helpers import createAccessToken, emailValidate, get_ts, password_validate
from apps.messages import Messages

message = Messages.message

login_limit = Config.LOGIN_ATTEMPT_LIMIT

# User States
STATUS_SUSPENDED = Config.USERS_STATUS['SUSPENDED']
STATUS_ACTIVE = Config.USERS_STATUS['ACTIVE']

# Users Roles
ROLE_ADMIN = Config.USERS_ROLES['ADMIN']
ROLE_USER = Config.USERS_ROLES['USER']

upload_folder_name = Config.UPLOAD_FOLDER
download_folder_name = Config.DOWNLOAD_FOLDER
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


login_manager.anonymous_user = Anonymous


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """ 
        Login View 
    """
    template_name = 'accounts/login.html'
    login_form = LoginForm(request.form)

    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        valid_email = emailValidate(username)

        if valid_email:
            user = User.find_by_email(username)
        else:
            # Locate user
            user = User.find_by_username(username)

        # if user not found
        if not user:
            ip_ban.add()
            return render_template(template_name,
                                   msg=message['wrong_user_or_password'],
                                   form=login_form)

        # Check user is suspended
        if STATUS_SUSPENDED == user.status:
            return render_template(template_name,
                                   msg=message['suspended_account_please_contact_support'],
                                   form=login_form)

        if user.failed_logins >= login_limit:
            user.status = STATUS_SUSPENDED
            user.save()
            return render_template(template_name,
                                   msg=message['suspended_account_maximum_nb_of_tries_exceeded'],
                                   form=login_form)

        # Check the password
        if user and not verify_pass(password, user.password):
            user.failed_logins += 1
            user.save()
            ip_ban.add()
            return render_template(template_name,
                                   msg=message['incorrect_password'],
                                   form=login_form)
        login_user(user)
        user.failed_logins = 0
        user.save()

        return redirect(url_for('home_blueprint.index'))

    if not current_user.is_authenticated:

        # we might have a redirect from OAuth
        msg = request.args.get('oautherr')

        if msg and 'suspended' in msg:
            msg = message['suspended_account_please_contact_support']

        return render_template(template_name,
                               form=login_form,
                               msg=msg)

    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/logout')
@login_required
def logout():
    """ Logout View """
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
        User register view
    """
    if current_user.username == "Guest":
        number_of_users = User.get_number_of_users()
        if number_of_users != 0:
            return render_template('home/page-403.html')
    elif current_user.is_authenticated:
        if current_user.role != ROLE_ADMIN:
            return render_template('home/page-403.html')

    # already logged in
    if current_user.is_authenticated:
        return redirect('/')

    template_name = 'accounts/register.html'
    create_account_form = CreateAccountForm(request.form)

    if 'register' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password_check']

        if password != password2:
            return render_template(template_name,
                                   msg=message['pwd_not_match'],
                                   success=False,
                                   form=create_account_form)

        # Check if username exists
        user = User.find_by_username(username)
        if user:
            return render_template(template_name,
                                   msg=message['username_already_registered'],
                                   success=False,
                                   form=create_account_form)

        # Check if email exists
        user = User.find_by_email(email)
        if user:
            return render_template(template_name,
                                   msg=message['email_already_registered'],
                                   success=False,
                                   form=create_account_form)

        valid_pwd = password_validate(password)
        if not valid_pwd:
            return render_template(template_name,
                                   msg=valid_pwd,
                                   success=False,
                                   form=create_account_form)

        user = User(**request.form)
        user.api_token = createAccessToken()
        user.api_token_ts = get_ts()
        user.save()

        # Force logout
        logout_user()

        # send signal for create profile
        user_saved_signals.send({"user_id": user.id, "email": user.email})

        return render_template(template_name,
                               msg=message['account_created_successfully'],
                               success=True,
                               form=create_account_form)

    else:
        return render_template(template_name, form=create_account_form)


# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
