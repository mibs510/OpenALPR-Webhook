from flask_mail import Message
from apps import mail
from apps.config import Config
default_sender = Config.MAIL_DEFAULT_SENDER


def send_email(to, subject, template):
    # with app.app_context():
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=default_sender
        )
    
    mail.send(msg)
    