import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager  

# --- Shared extension instances ---
db            = SQLAlchemy()
login_manager = LoginManager()
mail          = Mail()
csrf          = CSRFProtect()
limiter       = Limiter(key_func=get_remote_address)
migrate       = Migrate()
jwt           = JWTManager()  #  create JWT manager

def get_database_uri():
    return os.environ.get('DATABASE_URL', 'sqlite:///instance/user.db')

def create_app():
    """Application factory: create and configure the Flask app."""
    app = Flask(
        __name__,
        static_folder='frontend',
        template_folder='frontend',
        static_url_path='/static' 
    )

    # Secret key: random on every boot clears all cookies/sessions
    app.config['SECRET_KEY'] = os.urandom(32)

    # Core configuration (database, mail, JWT, etc.) 
    app.config.update(
        SQLALCHEMY_DATABASE_URI         = get_database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS  = False,
        MAIL_SERVER                     = os.environ.get('MAIL_SERVER'),
        MAIL_PORT                       = int(os.environ.get('MAIL_PORT', '587')),
        MAIL_USE_TLS                    = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true','1'),
        MAIL_USERNAME                   = os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD                   = os.environ.get('MAIL_PASSWORD'),
        JWT_SECRET_KEY                  = os.environ.get('JWT_SECRET_KEY', 'change-this-too'),
        JWT_ACCESS_TOKEN_EXPIRES        = int(os.environ.get('JWT_EXPIRES_S', 3600)),
        SESSION_COOKIE_SECURE           = True,
        SESSION_COOKIE_HTTPONLY         = True,
        SESSION_COOKIE_SAMESITE         = 'Lax',
        MAX_CONTENT_LENGTH              = 2 * 1024 * 1024,  # 2MB
        RATELIMIT_ENABLED               = False           # disable limits until ready
    )

    # Rate limiter storage backend (optional Redis) 
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        app.config['RATELIMIT_STORAGE_URI'] = redis_url

    #  Initialize extensions 
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)     # no-op while RATELIMIT_ENABLED=False
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)         # initialize JWTManager

    #  Flask-Login settings 
    login_manager.login_view          = 'auth.login'
    login_manager.login_message_category = 'error'

    #  Register blueprints 
    from .authentication import auth_bp
    from .profile        import profile_bp
    from .passwords      import bp as passwords_bp
    from .contact        import contact_bp

    app.register_blueprint(auth_bp)        # /auth/
    app.register_blueprint(profile_bp, url_prefix='/profile')    # /profile
    app.register_blueprint(passwords_bp)   # /passwords + /passwords/api
    app.register_blueprint(contact_bp)     # /contact

    return app
