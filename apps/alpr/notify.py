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

import enum
import logging
import smtplib
import ssl
from email.mime.text import MIMEText

from twilio.rest import Client

from apps.alpr.models.settings import TwilioNotificationSettings, EmailNotificationSettings


class Tag(enum.Enum):
    ACCOUNT = 'Account'
    ADMIN = 'Admin'
    AGENT = 'Agent'
    ALERT = 'Alert'
    CAMERA = 'Camera'
    SECURITY = 'Security'
    TEST = 'Test'


class Email:
    _settings = None
    tag = ""
    subject = ""
    body = ""
    recipients = []

    def __init__(self):
        self._settings = EmailNotificationSettings.get_settings()
        self.recipients = self._settings.recipients

    def send(self) -> bool:

        # Stop if Email is disabled
        if not self._settings.enabled:
            return False

        try:
            # Split the string to create a list: user1@example.com,user2@example.com ->
            # -> ['user1@example.com', 'user2@example.com']
            recipients = self._settings.recipients.split(',')

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self._settings.hostname, self._settings.port, context=context) as server:
                server.login(self._settings.username_email, self._settings.password)
                for recipient in recipients:
                    msg = MIMEText(self.body)
                    msg['To'] = recipient
                    msg['From'] = self._settings.username_email
                    msg['Subject'] = "[{}] {} - OpenALPR-Webhook".format(self.tag, self.subject)
                    server.login(self._settings.username_email, self._settings.password)
                    server.send_message(msg)
        except Exception as ex:
            logging.exception(ex)
            return False
        return True

    def send_test(self) -> None:
        try:
            self.tag = Tag.TEST.value
            self.subject = "SMTP Test"
            self.body = "This is a test 🧪 message from OpenALPR-Web🪝!"
            self.send()
        except Exception as ex:
            raise ex


class SMS:
    _settings = None
    msg = ""
    recipients = []

    def __init__(self):
        self._settings = TwilioNotificationSettings.get_settings()
        self.recipients = self._settings.recipients

    def send(self) -> None:
        try:
            # Split the string to create a list: +12345678901,+12345678901 ->
            # -> ['+12345678901', '+12345678901']
            recipients = self._settings.recipients.split(',')

            client = Client(self._settings.account_sid, self._settings.auth_token)

            for recipient in recipients:
                client.messages.create(to=recipient, from_=self._settings.phone_number, body=self.msg)
        except Exception as ex:
            raise ex

    def send_test(self) -> None:
        self.msg = "OpenALPR-Web🪝 Test 🧪".encode('utf-8')
        self.send()
