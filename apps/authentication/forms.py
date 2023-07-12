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

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired, EqualTo

from apps.authentication.models import User
from apps.authentication.util import verify_pass
from apps.helpers import password_validate


class LoginForm(FlaskForm):
    username = StringField('Username',
                           id='username_login',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])

    def validate(self):

        user = User.query.filter_by(username=self.username.data).first()

        if not user:
            # self.username.errors.append('Unknown email')
            return False

        if user and not verify_pass(self.password.data, user.password):
            # if not user.verify_pass(self.password.data):
            # self.password.errors.append('Invalid password')
            return False

        return True


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])
    email = StringField('Email', id='email_create',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='id_password1',
                             validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    password_check = PasswordField('Password Check',
                                   id='id_password2',
                                   validators=[DataRequired(), EqualTo('password', message="Passwords must match")])

    def validate(self):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            # self.email.errors.append("Email already registered")
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            # self.email.errors.append("Username already exists.")
            return False

        valid_pwd = password_validate(self.password.data)
        if not valid_pwd:
            return False

        return True


class UserProfileForm(FlaskForm):
    full_name = StringField('Full Name',
                            id='full_name_create',
                            validators=[DataRequired()])
    address = StringField('Address',
                          id='address_create',
                          validators=[DataRequired()])
    bio = StringField('Bio',
                      id='bio')
    zipcode = StringField('Zipcode',
                          id='zipcode_create')
    phone = StringField('Phone',
                        id='phone_create',
                        validators=[DataRequired()])
    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired()])
    website = StringField('Website',
                          id='website_create')
    image = StringField('Image',
                        id='image_create',
                        validators=[DataRequired()])
