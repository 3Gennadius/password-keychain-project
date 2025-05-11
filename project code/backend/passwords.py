from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import db, csrf, limiter
from .model import PasswordEntry
from .validation import validate_vault_entry, validate_vault_password_confirm
from .logging_utils import log_vault_entry_create, log_vault_entry_edit, log_vault_entry_delete

bp = Blueprint('passwords', __name__, url_prefix='/passwords')

# Server-rendered page
@bp.route('', methods=['GET'])
@login_required
@limiter.limit("20 per minute")
def list_entries():
    return render_template('manage-passwords.html')

# =======================
# JSON API Endpoints for Vault CRUD
# =======================

@bp.route('/api', methods=['GET'])
@login_required
@limiter.limit("60 per minute")
def api_list():
    entries = PasswordEntry.query.filter_by(user_id=current_user.user_id).all()
    return jsonify([e.to_dict() for e in entries]), 200

@bp.route('/api', methods=['POST'])
@login_required
@csrf.exempt
@limiter.limit("30 per minute")
def api_create():
    data = request.get_json() or {}
    errs = validate_vault_entry(
        data.get('website', ''), data.get('username', ''), data.get('password', '')
    )
    if errs:
        return jsonify(errors=errs), 400

    entry = PasswordEntry(user_id=current_user.user_id)
    entry.set_website(data.get('website', '').strip())
    entry.set_username(data.get('username', '').strip())
    entry.set_password(data.get('password', '').strip())

    db.session.add(entry)
    db.session.commit()
    log_vault_entry_create(current_user.username, data.get('website', '').strip())
    return jsonify(entry.to_dict()), 201

@bp.route('/api/<int:entry_id>', methods=['PUT'])
@login_required
@csrf.exempt
@limiter.limit("30 per minute")
def api_update(entry_id):
    data = request.get_json() or {}
    errs = validate_vault_entry(
        data.get('website', ''), data.get('username', ''), data.get('password', '')
    )
    if errs:
        return jsonify(errors=errs), 400

    entry = PasswordEntry.query.filter_by(
        user_id=current_user.user_id, entry_id=entry_id
    ).first_or_404()
    entry.set_website(data.get('website', entry.get_website()).strip())
    entry.set_username(data.get('username', entry.get_username()).strip())
    entry.set_password(data.get('password', entry.get_password()).strip())

    db.session.commit()
    log_vault_entry_edit(current_user.username, entry.get_website())
    return jsonify(entry.to_dict()), 200

@bp.route('/api/<int:entry_id>', methods=['DELETE'])
@login_required
@csrf.exempt
@limiter.limit("30 per minute")
def api_delete(entry_id):
    entry = PasswordEntry.query.filter_by(
        user_id=current_user.user_id, entry_id=entry_id
    ).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    return ('', 204)
