import glob
import os

from setuptools import setup
from version import __version__

if os.path.exists("README.md"):
    with open("README.md", "r") as fh:
        long_description = fh.read()


setup(
    name='OpenALPR-Webhook',
    version=__version__,
    platforms='linux',
    packages=['apps', 'apps/alpr', 'apps/alpr/ipban', 'apps/alpr/models', 'apps/alpr/routes', 'apps/alpr/routes/alert',
              'apps/alpr/routes/alerts', 'apps/alpr/routes/alerts/custom', 'apps/alpr/routes/alerts/rekor',
              'apps/alpr/routes/capture', 'apps/alpr/routes/search', 'apps/alpr/routes/settings',
              'apps/alpr/routes/settings/agents', 'apps/alpr/routes/settings/cameras',
              'apps/alpr/routes/settings/cameras/manufacturers', 'apps/alpr/routes/settings/general',
              'apps/alpr/routes/settings/maintenance', 'apps/alpr/routes/settings/maintenance/rq_dashboard',
              'apps/alpr/routes/settings/notifications', 'apps/alpr/routes/settings/profile',
              'apps/alpr/routes/settings/users', 'apps/alpr/routes/vehicle', 'apps/api', 'apps/authentication',
              'apps/db', 'apps/exceptions', 'apps/home', 'apps/static/assets', 'apps/templates',
              'apps/uploads', 'nginx'],
    url='https://github.com/mibs510/OpenALPR-Webhook',
    license='MIT',
    author='Connor McMillan',
    author_email='connor@mcmillan.website',
    description='OpenALPR-Webhook is a self-hosted web application that accepts Rekor Scout™ POST data allowing longer '
                'data retention. It was designed with an emphasis on security to meet organization/business needs.',
    long_description=long_description,
    python_requires=">=3.10",
    install_requires=['aiohttp==3.8.4', 'aiohttp-retry==2.8.3', 'aiosignal==1.3.1', 'alembic==1.10.4',
                      'aniso8601==9.0.1', 'argcomplete==3.0.8', 'arrow==1.2.3', 'astral==2.2', 'async-timeout==4.0.2',
                      'asyncio==3.4.3', 'attrs==23.1.0', 'blinker==1.4', 'certifi==2022.12.7', 'cfgv==3.3.1',
                      'charset-normalizer==3.1.0', 'click==7.1.2', 'colorama==0.4.4', 'Cython==0.29.34',
                      'decli==0.6.1', 'distlib==0.3.6', 'dnspython==2.3.0', 'email-validator==2.0.0.post2',
                      'filelock==3.12.0', 'Flask==1.1.4', 'flask-ipban==1.1.5', 'Flask-Login==0.6.2',
                      'Flask-Mail==0.9.1', 'Flask-Migrate==2.6.0', 'Flask-Minify==0.41', 'flask-paginate==2022.1.8',
                      'flask-restx==0.5.1', 'Flask-Script==2.0.6', 'Flask-SQLAlchemy==2.5.1', 'Flask-WTF==1.0.0',
                      'frozenlist==1.3.3', 'greenlet==2.0.2', 'gunicorn==20.1.0', 'htmlmin==0.1.12', 'identify==2.5.24',
                      'idna==3.4', 'importlib-metadata==6.6.0', 'ipc-sun-sync==0.2.3', 'itsdangerous==1.1.0',
                      'Jinja2==2.11.3', 'jsmin==3.0.1', 'jsonschema==4.17.3', 'lesscpy==0.15.1', 'Mako==1.2.4',
                      'MarkupSafe==2.0.1', 'marshmallow==3.14.1', 'marshmallow-sqlalchemy==0.22.3', 'multidict==6.0.4',
                      'nodeenv==1.8.0', 'oauthlib==3.2.2', 'packaging==23.1', 'phonenumbers==8.13.11',
                      'platformdirs==3.5.1', 'ply==3.11', 'progressbar2==4.2.0', 'prompt-toolkit==3.0.38',
                      'psutil==5.9.5', 'pycountry==22.3.5', 'PyJWT==2.6.0', 'pyrsistent==0.19.3',
                      'python-dateutil==2.8.2', 'python-utils==3.7.0', 'pytimeparse==1.1.8', 'pytz==2022.1',
                      'PyYAML==6.0', 'questionary==1.10.0', 'random-password-generator==2.2.0', 'rcssmin==1.1.1',
                      'redis==4.4.4', 'Redis-Sentinel-Url==1.0.1', 'requests==2.28.2', 'requests-oauthlib==1.3.1',
                      'rq==1.12.0', 'setproctitle==1.3.2', 'six==1.16.0', 'SQLAlchemy==1.4.29',
                      'sqlalchemy-json==0.5.0', 'termcolor==2.3.0', 'tomlkit==0.11.8', 'twilio==8.0.0',
                      'typing_extensions==4.5.0', 'unqlite==0.9.3', 'urllib3==1.26.15', 'URLObject==2.4.3',
                      'virtualenv==20.23.0', 'wcwidth==0.2.6', 'Werkzeug==1.0.1', 'WTForms==3.0.0', 'xxhash==3.2.0',
                      'yarl==1.9.2', 'zipp==3.15.0'],
    classifiers=['Development Status :: 4 - Beta',
                 'Framework :: Flask',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3.10'],
)

if __name__ == "__main__":
    pass
