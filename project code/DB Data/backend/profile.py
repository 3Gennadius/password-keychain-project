import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend import db, csrf
from backend.validation import validate_avatar, validate_username, validate_email, validate_password_change

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def get_avatar_upload_folder():
    return os.path.join(current_app.instance_path, 'avatars')

@profile_bp.route('', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def profile():
    errors = {}

    if request.method == 'POST':
        try:
            with db.session.begin():
                avatar = request.files.get('profile_image')
                if avatar and avatar.filename:
                    err = validate_avatar(avatar)
                    if err:
                        errors['avatar'] = err
                    else:
                        fn = secure_filename(f"{current_user.id}_{avatar.filename}")
                        avatar_folder = get_avatar_upload_folder()
                        os.makedirs(avatar_folder, exist_ok=True)
                        path = os.path.join(avatar_folder, fn)
                        avatar.save(path)
                        current_user.profile_image = fn  # Store filename only

                uname = request.form.get('username', '')
                e = validate_username(uname)
                if e:
                    errors['username'] = e
                else:
                    current_user.username = uname.strip()

                email = request.form.get('email', '')
                e = validate_email(email)
                if e:
                    errors['email'] = e
                else:
                    current_user.email = email.strip()

                old_pw = request.form.get('old-master-password', '')
                new_pw = request.form.get('new-master-password', '')
                confirm_pw = request.form.get('confirm-new-master-password', '')
                stored = current_user.get_master_password()
                pw_errors = validate_password_change(old_pw, new_pw, confirm_pw, stored)
                errors.update(pw_errors)
                if not pw_errors and (old_pw or new_pw or confirm_pw):
                    current_user.set_master_password(new_pw.strip())

                if errors:
                    raise ValueError("Validation errors")
        except Exception:
            db.session.rollback()
            for msg in errors.values():
                flash(msg, 'error')
        else:
            flash('Your profile has been updated successfully.', 'success')
            return redirect(url_for('profile.profile'))

    return render_template(
        'profile.html',
        current_user=current_user,
        decrypted_password=current_user.get_master_password(),
        errors=errors
    )

@profile_bp.route('/avatar/<filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(get_avatar_upload_folder(), secure_filename(filename))
