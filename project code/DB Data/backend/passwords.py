from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend import db, csrf
from backend.model import PasswordEntry
from backend.validation import (
    sanitize_label, validate_label,
    sanitize_entry_username, validate_entry_username,
    validate_vault_password
)

passwords_bp = Blueprint('passwords', __name__, url_prefix='/passwords')

@passwords_bp.route('', methods=['GET'])
@login_required
def list_passwords():
    entries = PasswordEntry.query.filter_by(user_id=current_user.user_id).all()
    display = [{
        'entry_id': e.entry_id,
        'label': e.label,
        'username': e.get_username(),
        'password': e.get_password()
    } for e in entries]
    return render_template('passwords.html', entries=display)

@passwords_bp.route('/add', methods=['POST'])
@login_required
@csrf.exempt
def add_password():
    raw_label = request.form.get('website_name', '')
    raw_user = request.form.get('entry_username', '')
    raw_password = request.form.get('entry_password', '')

    label = sanitize_label(raw_label)
    username = sanitize_entry_username(raw_user)
    password = raw_password

    label_error = validate_label(label)
    user_error = validate_entry_username(username)
    password_error = validate_vault_password(password)

    if label_error:
        flash(label_error, 'error')
        return redirect(url_for('passwords.list_passwords'))
    if user_error:
        flash(user_error, 'error')
        return redirect(url_for('passwords.list_passwords'))
    if password_error:
        flash(password_error, 'error')
        return redirect(url_for('passwords.list_passwords'))

    entry = PasswordEntry(user_id=current_user.user_id, label=label)
    entry.set_username(username)
    entry.set_password(password)
    db.session.add(entry)
    db.session.commit()

    flash('New vault entry added.', 'success')
    return redirect(url_for('passwords.list_passwords'))

@passwords_bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
@csrf.exempt
def delete_password(entry_id):
    entry = PasswordEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.user_id:
        flash('Unauthorized operation.', 'error')
    else:
        db.session.delete(entry)
        db.session.commit()
        flash('Vault entry deleted.', 'success')
    return redirect(url_for('passwords.list_passwords'))
