import datetime
import logging
import os
import subprocess
import uuid
import re

import pytz
from colorama import Fore, Style
from apps.authentication.models import User, UserProfile
import ipaddress
from apps.messages import Messages
from functools import wraps
from flask import request
from uuid import uuid4
import time
import phonenumbers

message = Messages.message


def netstat() -> float:
    try:
        netstat = subprocess.Popen(['netstat', '-aon'], stdout=subprocess.PIPE)
        grep_3565 = subprocess.Popen(['grep', '3565'], stdin=netstat.stdout, stdout=subprocess.PIPE)
        grep_time_wait = subprocess.Popen(['grep', 'TIME_WAIT'], stdin=grep_3565.stdout, stdout=subprocess.PIPE)
        tail_n_1 = subprocess.Popen(['tail', '-n1'], stdin=grep_time_wait.stdout, stdout=subprocess.PIPE)
        awk = subprocess.Popen(['awk', '{print $8}'], stdin=tail_n_1.stdout, stdout=subprocess.PIPE)

        stdout, stderr = awk.communicate()
        stdout = stdout.decode('utf-8')
        logging.debug("stdout = {}".format(stdout))

        if awk.returncode == 0:
            if stdout != "":
                stdout = stdout.split('/')
                seconds = stdout[0].strip('(')
                logging.debug("seconds = {}".format(seconds))
                return float(seconds)
            return 0.00
        return 0.00
    except Exception:
        return 0.00


def setChoices(current_user, user_ids: []) -> []:
    users = User.query
    choices = []
    for user in users:
        if user.username != current_user.username:
            user_profile = UserProfile.find_by_user_id(user.id)
            selected = False
            if user_ids is not None:
                if str(user.id) in user_ids:
                    selected = True
            if user_profile.full_name != "":
                label = user_profile.full_name + " (" + user.email + ")"
            else:
                label = user.username + " (" + user.email + ")"
            choices.append({
                'value': user.id,
                'label': label,
                'selected': selected
            })
    return choices


def shorten_description(description: str, n=20) -> str:
    split_description = str(description).split(' ')
    shorten_desc = None

    if len(split_description) <= n:
        return description

    if len(split_description) > n:
        for i in range(n):
            if i == 0:
                shorten_desc = split_description[i] + " "
            elif i != n - 1:
                shorten_desc = shorten_desc + split_description[i] + " "
            elif i == n - 1:
                shorten_desc = shorten_desc + " " + split_description[i] + "..."

    return shorten_desc


class Timezone:
    user = None
    profile = None
    msecs = False

    def __init__(self, current_user: str, msecs=False):
        # Get timezone from the user settings
        self.user = User.find_by_username(str(current_user))
        self.profile = UserProfile.find_by_id(self.user.id)
        self.msecs = msecs

    def astimezone(self, utc: datetime) -> str:

        if type(utc) is int:
            utc = datetime.datetime.utcfromtimestamp(utc / 1000)

        if self.msecs:
            schema = "%b %d %Y %I:%M:%S:%f %p %Z"
        else:
            schema = "%b %d %Y %I:%M:%S %p %Z"

        if self.profile:
            return utc.replace(tzinfo=datetime.timezone.utc).astimezone(tz=pytz.timezone(self.profile.timezone)). \
                strftime(schema)
        else:
            return utc

    def day(self, utc: datetime) -> str:
        if type(utc) is int:
            utc = datetime.datetime.utcfromtimestamp(utc / 1000)

        return utc.replace(tzinfo=datetime.timezone.utc).astimezone(tz=pytz.timezone(self.profile.timezone)). \
            strftime("%d")

    def month(self, utc: datetime) -> str:
        if type(utc) is int:
            utc = datetime.datetime.utcfromtimestamp(utc / 1000)

        return utc.replace(tzinfo=datetime.timezone.utc).astimezone(tz=pytz.timezone(self.profile.timezone)). \
            strftime("%b")


# Thanks to Tim Pietzcker @stackoverflow.com
# https://stackoverflow.com/a/2532344
def is_valid_hostname(hostname: str) -> bool:
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_port(port: int) -> bool:
    try:
        # Try casting it
        if 1 <= port <= 65535:
            return True
    except Exception:
        return False


def are_valid_email_recipients(recipients: str) -> bool:
    recipients = recipients.split(',')
    for recipient in recipients:
        if not emailValidate(recipient):
            return False
    return True


def are_valid_sms_recipients(recipients: str) -> bool:
    recipients = recipients.split(',')
    for recipient in recipients:
        try:
            if not phonenumbers.is_valid_number(phonenumbers.parse(recipient)):
                return False
        except:
            return False
    return True


def get_ts():
    return int(time.time())


def password_validate(password):
    """ password validate """
    msg = ''
    while True:
        if len(password) < 6:
            msg = "Make sure your password is at lest 6 letters"
            return msg
        elif re.search('[0-9]', password) is None:
            msg = "Make sure your password has a number in it"
            return msg
        elif re.search('[A-Z]', password) is None:
            msg = "Make sure your password has a capital letter in it"
            return msg
        else:
            msg = True
            break

    return True


def emailValidate(email):
    """ validate email  """
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def mkdir(folder_name):
    if not os.path.exists(f'{folder_name}'):
        os.makedirs(f'{folder_name}')

    return folder_name


def unique_file_name(file_name):
    """ for Unique file name"""
    file_uuid = uuid.uuid4()
    return f'{file_uuid}-{file_name}'


def errorColor(error):
    """ for terminal input error color """
    print(Fore.RED + f'{error}')
    print(Style.RESET_ALL)
    return True


def splitUrlGetFilename(url):
    """ image url split and get file name  """
    return url.split('/')[-1]


def expectedValue(data):
    """ key get values """
    values = []
    for k, v in data.items():
        values.append(f'{v}.({k})')

    return ",".join(values)


def createAccessToken():
    """ create access token w"""
    rand_token = uuid4()

    return f"{str(rand_token)}"


# token validate
def token_required(f):
    """ check token """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "error": "Unauthorized"
            }, 401
        try:
            current_user = User.find_by_api_token(token)
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "error": "Unauthorized"
                }, 401
            # if not current_user["active"]:
            #     abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "error": str(e)
            }, 500

        return f(current_user, **kwargs)

    return decorated
