# backend/__init__.py

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Shared extension instances
db            = SQLAlchemy()
login_manager = LoginManager()
mail          = Mail()
csrf          = CSRFProtect()

# Choose limiter storage at import time so blueprints can import it:
_use_redis = os.getenv('USE_REDIS_LIMITER', 'false').lower() in ('true','1')
_redis_url = os.getenv('REDIS_URL', '').strip()

if _use_redis and _redis_url:
    limiter = Limiter(key_func=get_remote_address, storage_uri=_redis_url)
    logging.info(f"Flask-Limiter: using Redis at {_redis_url}")
else:
    limiter = Limiter(key_func=get_remote_address)  # in-memory fallback
    if _use_redis:
        logging.warning("USE_REDIS_LIMITER=true but REDIS_URL is missing/invalid; falling back to in-memory limiter")
    else:
        logging.info("Flask-Limiter: using in-memory storage (disable USE_REDIS_LIMITER to silence)")

def get_database_uri():
    uri = os.getenv('DATABASE_URL', '').strip()
    if not uri or 'DB_PORT' in uri or '//' not in uri:
        user = os.getenv('DB_USER', '')
        pwd  = os.getenv('DB_PASS', '')
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '3306')
        name = os.getenv('DB_NAME', 'dunkey')
        uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}"
    return uri

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Core config
    app.config.from_mapping(
        SECRET_KEY                    = os.environ.get('FLASK_SECRET_KEY', 'dev-secret'),
        SQLALCHEMY_DATABASE_URI       = get_database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        MAIL_SERVER                   = os.environ.get('MAIL_SERVER'),
        MAIL_PORT                     = int(os.environ.get('MAIL_PORT', '587')),
        MAIL_USE_TLS                  = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true','1'),
        MAIL_USERNAME                 = os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD                 = os.environ.get('MAIL_PASSWORD'),
        SESSION_COOKIE_SECURE         = True,
        SESSION_COOKIE_HTTPONLY       = True,
        SESSION_COOKIE_SAMESITE       = 'Lax',
        MAX_CONTENT_LENGTH            = 2 * 1024 * 1024  # 2MB upload limit
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'

    # Register blueprints
    from backend.authentication import auth_bp
    from backend.profile        import profile_bp
    from backend.passwords      import passwords_bp
    from backend.contact        import contact_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(passwords_bp)
    app.register_blueprint(contact_bp)

    return app

from backend.model import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
