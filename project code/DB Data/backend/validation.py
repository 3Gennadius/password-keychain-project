import re

def sanitize_username(username: str) -> str:
    """
    Remove any unwanted characters and trim whitespace.
    Allows alphanumeric characters, underscores, and periods.
    """
    return re.sub(r'[^a-zA-Z0-9_.]', '', username).strip()

def is_valid_email(email: str) -> bool:
    """
    Validate email using regex.
    """
    email_regex = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(email_regex, email) is not None

def is_strong_password(password: str) -> bool:
    """
    Enforce password to have at least:
    - 8 characters
    - 1 uppercase letter
    - 1 lowercase letter
    - 1 number
    - 1 special character
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[\W_]', password):  # Special characters
        return False
    return True

def sanitize_label(label: str) -> str:
    """
    Sanitize website label for password storage.
    """
    return label.strip()

def validate_label(label: str) -> str:
    if not label:
        return "Label cannot be empty."
    if len(label) > 255:
        return "Label is too long."
    return ""

def sanitize_entry_username(username: str) -> str:
    return username.strip()

def validate_entry_username(username: str) -> str:
    if not username:
        return "Username cannot be empty."
    if len(username) > 150:
        return "Username is too long."
    return ""

def validate_vault_password(password: str) -> str:
    if not password:
        return "Password cannot be empty."
    if not is_strong_password(password):
        return (
            "Password must be at least 8 characters long, "
            "and include uppercase, lowercase, a number, and a symbol."
        )
    return ""

def validate_avatar(file) -> str:
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename:
        return "Invalid file type."
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return "Invalid file extension."
    if file.content_length and file.content_length > 2 * 1024 * 1024:
        return "File is too large (max 2MB)."
    return ""

def validate_username(username: str) -> str:
    if not sanitize_username(username):
        return "Invalid username."
    if len(username) > 45:
        return "Username is too long."
    return ""

def validate_email(email: str) -> str:
    if not is_valid_email(email):
        return "Invalid email format."
    if len(email) > 95:
        return "Email is too long."
    return ""

def validate_password_change(old_pw: str, new_pw: str, confirm_pw: str, stored_pw: str) -> dict:
    errors = {}
    if old_pw or new_pw or confirm_pw:
        if old_pw != stored_pw:
            errors['old_password'] = "Old master password is incorrect."
        if new_pw != confirm_pw:
            errors['new_password'] = "New passwords do not match."
        if not is_strong_password(new_pw):
            errors['new_password_strength'] = (
                "New password must be at least 8 characters long, "
                "with uppercase, lowercase, number, and symbol."
            )
    return errors
