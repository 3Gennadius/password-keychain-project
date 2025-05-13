import os
from dotenv import load_dotenv
load_dotenv()
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
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()
jwt = JWTManager()

def get_database_uri():
    db_user = os.environ.get('DB_USER', 'root')
    db_pass = os.environ.get('DB_PASSWORD', 'kalialex1?')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_name = os.environ.get('DB_NAME', 'dunkey_db')
    
    return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"

def create_app():
    """Application factory: create and configure the Flask app."""
    app = Flask(
        __name__,
        static_folder='frontend',
        template_folder='frontend',
        static_url_path='/static' 
    )

    # Use a fixed secret key for session consistency
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))

    # Core configuration
    app.config.update(
        SQLALCHEMY_DATABASE_URI=get_database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTION={"pool_pre_ping": True},
        MAIL_SERVER=os.environ.get('MAIL_SERVER'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT', '587')),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true','1'),
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'change-this-too'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.environ.get('JWT_EXPIRES_S', 3600)),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # 2MB
        RATELIMIT_ENABLED=False
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'  # Blueprint-aware endpoint name
    login_manager.login_message_category = 'error'
    login_manager.session_protection = "strong"  # Enhanced session security

    # Register blueprints
    from .authentication import auth_bp
    from .profile import profile_bp
    from .passwords import bp as passwords_bp
    from .contact import contact_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')  # Add url_prefix
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(passwords_bp)
    app.register_blueprint(contact_bp)

    # Add after_request hook for CSRF token rotation
    @app.after_request
    def rotate_csrf_token(response):
        if response.status_code == 200:
            csrf.protect()  # Rotate CSRF token after successful requests
        return response

    return app