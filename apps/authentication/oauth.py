import os
from flask_login import current_user, login_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import github, make_github_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.twitter import twitter, make_twitter_blueprint
from sqlalchemy.orm.exc import NoResultFound
from apps.authentication.signals import user_saved_signals
from apps.helpers import createAccessToken, get_ts
from apps.config import Config
from .models import User, db, OAuth
from flask import redirect, url_for

STATUS_SUSPENDED = Config.USERS_STATUS['SUSPENDED']

github_blueprint = make_github_blueprint(
    client_id=Config.GITHUB_ID,
    client_secret=Config.GITHUB_SECRET,
    scope = 'user',
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,        
    ),   
)

twitter_blueprint = make_twitter_blueprint(
    api_key=Config.TWITTER_ID,
    api_secret=Config.TWITTER_SECRET,
    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),
)

@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    info = github.get("/user")

    if info.ok:

        account_info = info.json()
        username     = account_info["login"]

        query = User.query.filter_by(oauth_github=username)
        try:

            user = query.one()

            # Take into account the current user state
            if STATUS_SUSPENDED == user.status:
                return redirect('/login?oautherr=suspended')

            login_user(user)

        except NoResultFound:

            # Save to db
            user              = User()
            user.username     = '(gh)' + username
            user.oauth_github = username
            user.api_token    = createAccessToken()
            user.api_token_ts = get_ts()
            user.save()

            # send signal for create profile
            user_saved_signals.send({"user_id":user.id, "email": user.email})
            login_user(user)

@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    info = twitter.get("account/settings.json")

    if info.ok:
        account_info = info.json()
        username     = account_info["screen_name"]

        query = User.query.filter_by(oauth_twitter=username)
        try:

            user = query.one()

            # Take into account the current user state
            if STATUS_SUSPENDED == user.status:
                return redirect('/login?oautherr=suspended')

            login_user(user)
        
        except NoResultFound:

            # Save to db
            user              = User()
            user.username     = '(tw)' + username
            user.oauth_github = username
            user.api_token    = createAccessToken()
            user.api_token_ts = get_ts()
            user.save()

            # send signal for create profile
            user_saved_signals.send({"user_id":user.id, "email": user.email})
            login_user(user)
