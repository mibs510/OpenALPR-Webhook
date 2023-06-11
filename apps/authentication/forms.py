from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, DataRequired, EqualTo, InputRequired

from apps.authentication.models import User
from apps.helpers import password_validate
from apps.authentication.util import verify_pass


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

