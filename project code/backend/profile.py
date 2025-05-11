from flask import Blueprint, current_app, request, redirect, flash, jsonify, send_from_directory, abort
from flask_login import login_required, current_user
from . import db, csrf, limiter
from werkzeug.utils import secure_filename
from .logging_utils import log_update_credentials, log_update_password, log_update_email
from .model import User
import os

from .validation import (
    allowed_file,
    sanitize_username,
    is_valid_email,
    is_strong_password,
    validate_avatar
)


profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
FE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
AVATAR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'avatars')
os.makedirs(AVATAR_DIR, exist_ok=True)



@profile_bp.route('/avatars/<filename>')
@login_required
def serve_avatar(filename):
    if filename != current_user.avatar_path:
        abort(403)  # Forbidden
    return send_from_directory(AVATAR_DIR, filename)

@profile_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No avatar file provided.', 'error')
        return redirect('/profile.html')

    file = request.files['avatar']

    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect('/profile.html')

    #  Validate avatar and generate safe filename
    try:
        filename = validate_avatar(file, current_user.user_id)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect('/profile.html')

    #  Delete old avatar if it exists
    if current_user.avatar_path:
        old_avatar_path = os.path.join(AVATAR_DIR, current_user.avatar_path)
        if os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)

    #  Save the new avatar
    os.makedirs(AVATAR_DIR, exist_ok=True)
    file_path = os.path.join(AVATAR_DIR, filename)
    file.save(file_path)

    #  Update database
    current_user.avatar_path = filename
    db.session.commit()

    flash('Avatar uploaded successfully.', 'success')
    return redirect('/profile.html')

@profile_bp.route('', methods=['GET'])
@login_required
def profile_page():
    return send_from_directory(FE, 'profile.html')


@profile_bp.route('/api', methods=['GET'])
@login_required
def api_profile():
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'avatar_path': current_user.avatar_path or 'avatars/default.png'
    }), 200

@profile_bp.route('/update-credentials', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
@login_required
def update_credentials():
    form = request.form
    new_username = sanitize_username(form.get('new_username', '').strip())
    new_email = form.get('new_email', '').strip().lower()
    confirm = form.get('confirm_profile_change') == 'on'

    if not confirm:
        flash('You must confirm changes.', 'error')
        return redirect('/profile.html')

    if new_username and new_username != current_user.username:
        exists = db.session.query(
            db.exists().where(db.func.lower(User.username) == new_username.lower())
        ).scalar()
        if exists:
            flash('Username already taken.', 'error')
            return redirect('/profile.html')
        current_user.username = new_username

    if new_email and new_email != current_user.email:
        if not is_valid_email(new_email):
            flash('Invalid email address.', 'error')
            return redirect('/profile.html')
        current_user.email = new_email

    db.session.commit()
    old_email = current_user.email
    current_user.email = new_email
    db.session.commit()
    log_update_email(current_user.username, old_email, new_email)
    log_update_credentials(current_user.username)
    flash('Profile updated successfully.', 'success')
    return redirect('/profile.html')


@profile_bp.route('/change-password', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
@login_required
def change_password():
    form = request.form
    old_pw = form.get('old_password', '').strip()
    new_pw = form.get('new_password', '').strip()
    confirm_pw = form.get('confirm_password', '').strip()

    if not current_user.check_login_password(old_pw):
        flash('Current password is incorrect.', 'error')
        return redirect('/profile.html')

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'error')
        return redirect('/profile.html')

    if not is_strong_password(new_pw):
        flash('New password is not strong enough. Must be ≥8 chars, include uppercase, lowercase, digit, and symbol.', 'error')
        return redirect('/profile.html')

    current_user.set_login_password(new_pw)
    db.session.commit()
    log_update_password(current_user.username)
    flash('Password changed successfully.', 'success')
    return redirect('/profile.html')



@csrf.exempt
@limiter.limit("5 per minute")
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect('/profile.html')

    file = request.files['avatar']
    if file.filename == '':
        flash('No selected file.', 'error')
        return redirect('/profile.html')

    try:
        # Validate and generate a secure filename
        filename = validate_avatar(file, current_user.user_id)
        avatar_path = os.path.join(AVATAR_DIR, filename)

        # Remove old avatar if it's not the default
        old_avatar = current_user.avatar_path
        if old_avatar and old_avatar != 'avatars/default.png':
            old_avatar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', old_avatar)
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

        # Save new avatar
        file.save(avatar_path)
        current_user.avatar_path = f"avatars/{filename}"
        db.session.commit()

        if request.method == 'POST':
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(AVATAR_DIR, filename))

                #  Update the user's avatar path and save it to the DB
                current_user.avatar_path = f"avatars/{filename}"
                db.session.commit()

                flash('Avatar uploaded successfully.', 'success')
                return redirect('/profile.html')
        

        flash('Avatar uploaded successfully.', 'success')
    except ValueError as ve:
        flash(str(ve), 'error')
    except Exception as e:
        current_app.logger.error(f"Failed to upload avatar: {e}")
        flash('Failed to upload avatar.', 'error')

    return redirect('/profile.html')

@profile_bp.route('/dark-mode', methods=['GET'])
@login_required
def get_dark_mode():
    return jsonify({'dark_mode': current_user.prefers_dark_mode})

# POST Route
@profile_bp.route('/dark-mode', methods=['POST'])
@csrf.exempt
@login_required
def set_dark_mode():
    preference = request.json.get('dark_mode', False)
    current_user.prefers_dark_mode = bool(preference)
    db.session.commit()
    return jsonify({'status': 'success', 'dark_mode': current_user.prefers_dark_mode})
