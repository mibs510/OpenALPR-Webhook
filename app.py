from apps import create_app, db
from apps.config import config_dict
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_minify import Minify
import os

# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

# Load the configuration using the default values
app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)
app.config['ENV'] = get_config_mode.capitalize()
Migrate(app, db)

# DB Migration
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)


if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG))
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE')
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)


if __name__ == "__main__":
    with app.app_context():
        app.run(host="0.0.0.0", port=8080)
