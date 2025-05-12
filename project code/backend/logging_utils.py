import logging
import os
from logging.handlers import TimedRotatingFileHandler
from flask import request, jsonify
from flask_limiter.errors import RateLimitExceeded

# Create logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logger
logger = logging.getLogger('vault_app')
logger.setLevel(logging.INFO)

file_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_dir, "vault_app.log"),
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def init_logging(app):
    """Attach rate limit logging to Flask app."""
    app.logger.handlers.extend(logger.handlers)

    @app.errorhandler(RateLimitExceeded)
    def rate_limit_handler(e):
        app.logger.warning(
            "RATE LIMIT EXCEEDED at endpoint=%s from IP=%s",
            request.path,
            request.remote_addr
        )
        return jsonify(error="Too many requests"), 429

# Manual Logging Methods 

def log_login_failed(identifier: str):
    logger.warning(f"LOGIN FAILED for identifier='{identifier}' from IP={request.remote_addr}")

def log_login_success(username: str):
    logger.info(f"User '{username}' successfully logged in.")

def log_register(username: str, email: str):
    logger.info(f"New user registered. Username: '{username}', Email: '{email}'.")

def log_update_credentials(username: str):
    logger.info(f"User '{username}' updated their credentials.")

def log_update_password(username: str):
    logger.info(f"User '{username}' changed their password.")

def log_update_email(username: str, old_email: str, new_email: str):
    logger.info(f"User '{username}' changed email from '{old_email}' to '{new_email}'.")

def log_vault_entry_create(username: str, entry_website: str):
    logger.info(f"User '{username}' created a vault entry websiteed '{entry_website}'.")

def log_vault_entry_edit(username: str, entry_website: str):
    logger.info(f"User '{username}' edited a vault entry websiteed '{entry_website}'.")

def log_vault_entry_delete(username: str, entry_website: str):
    logger.info(f"User '{username}' deleted a vault entry websiteed '{entry_website}'.")
