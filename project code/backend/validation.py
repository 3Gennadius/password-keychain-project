import re
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import os
from mimetypes import guess_type
import filetype

# General Validation Configs
MAX_AVATAR_SIZE = 512 * 1024  # 512 KB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# Login & Registration Validation
def sanitize_username(username: str) -> str:
    """Strip everything except letters, digits, underscores, and dots."""
    return re.sub(r'[^a-zA-Z0-9_.]', '', username).strip()

def is_valid_email(email: str) -> bool:
    """Check email validity with simple regex."""
    return bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email))

def is_strong_password(password: str) -> bool:
    """Ensure password is strong enough."""
    return bool(re.fullmatch(
        r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}', password
    ))


# Password Change Validation
def validate_password_change(
    old_password: str,
    new_password: str,
    confirm_password: str,
    stored_hash: str
) -> dict:
    """Validate password change process."""
    from werkzeug.security import check_password_hash

    errors = {}

    if not old_password or not check_password_hash(stored_hash, old_password):
        errors['old_password'] = 'Current password is incorrect.'

    if new_password != confirm_password:
        errors['confirm_password'] = 'New passwords do not match.'

    if not is_strong_password(new_password):
        errors['new_password'] = (
            'New password must be at least 8 characters long, include '
            'uppercase and lowercase letters, a digit, and a symbol.'
        )

    return errors


# Contact Form Validation
def validate_contact(name: str, email: str, message: str) -> dict:
    errors = {}
    if not name.strip():
        errors['name'] = 'Name is required.'
    if not is_valid_email(email):
        errors['email'] = 'A valid e-mail is required.'
    if not message.strip():
        errors['message'] = 'Message cannot be empty.'
    if len(message) > 1000:
        errors['message'] = 'Message is too long.'
    return errors


# Vault Entry Validation
def validate_vault_entry(entry_website: str, entry_username: str, entry_password: str) -> dict:
    errors = {}
    if not entry_website.strip():
        errors['website'] = 'Entry website is required.'
    if not entry_username.strip():
        errors['entry_username'] = 'Entry username is required.'
    if not entry_password:
        errors['entry_password'] = 'Entry password is required.'
    return errors

def validate_vault_password_confirm(password: str, confirm_password: str) -> dict:
    errors = {}
    if password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'
    return errors


# Avatar Upload Validation
def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_avatar(file_storage, user_id: int) -> str:
    """Validate avatar file and generate a safe, unique filename for storage."""

    filename = secure_filename(file_storage.filename)
    if not filename:
        raise ValueError('Invalid filename.')

    ext = filename.rsplit('.', 1)[1].lower()

    # Extension Validation
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError('Unsupported image type.')

    # Size Validation
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    if size > MAX_AVATAR_SIZE:
        raise ValueError('Avatar must be under 512KB.')
    file_storage.seek(0)  # Reset pointer after size check

    # MIME Type Validation
    mime_type, _ = guess_type(filename)
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError('Invalid image content type.')

    # Generate unique, safe filename (e.g., 15_avatar.png)
    unique_filename = f"{user_id}_avatar.{ext}"
    return unique_filename

    #This is used to validate vault entries for their sgrength and find  entries with same username/ same password

def flag_weak_entries(entries: list[dict]) -> list[dict]:
    flagged_entries = []
    passwords = [e['password'] for e in entries]
    usernames = [e['username'] for e in entries]

    for entry in entries:
        username = entry['username']
        password = entry['password']

        is_weak = (
            not is_strong_password(password) or
            username == password or
            passwords.count(password) > 1 or
            usernames.count(username) > 1
        )

        flagged_entries.append({
            'username': username,
            'password': password,
            'is_weak': is_weak
        })

    return flagged_entries
