from itsdangerous import URLSafeTimedSerializer
from apps.config import Config
secret_key = Config.SECRET_KEY
secret_pwd = Config.SECURITY_PASSWORD_SALT


def generate_confirmation_token(email):
    """ generate token"""
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=secret_pwd)


def confirm_token(token, expiration=3600):
    """ confirm token """
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(
            token,
            salt=secret_pwd,
            max_age=expiration
        )
    except:
        return False
    return email
