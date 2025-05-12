import os
from flask import Blueprint, jsonify, request, redirect, redirect, flash, current_app, send_from_directory, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token
from . import db, csrf, limiter
from .model import User
from .validation import sanitize_username, is_valid_email, is_strong_password
from flask_bcrypt import generate_password_hash, check_password_hash
from .logging_utils import log_login_failed, log_login_success, log_register

FE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/userinfo', methods=['GET'])
@login_required
def userinfo():
    return jsonify({
        'success': True,
        'username': current_user.username
    })

@auth_bp.route('/register', methods=['GET', 'POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect('/dashboard.html')

    if request.method == 'POST':
        form     = request.form
        username = sanitize_username(form.get('username', ''))
        email    = form.get('email', '').strip().lower()
        password = form.get('password', '')
        confirm  = form.get('confirm_password', '')

        if not username:
            flash('Username is required.', 'error')
            return redirect('/register.html')
        if not is_valid_email(email):
            flash('Invalid email address.', 'error')
            return redirect('/register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect('/register.html')
        if not is_strong_password(password):
            flash('Password must be at least 8 chars and include uppercase, lowercase, a digit, and a symbol.', 'error')
            return redirect('/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect('/register.html')

        user = User(username=username, email=email)
        user.password_hash = generate_password_hash(password).decode('utf-8')
        user.encrypted_master_password = None
        db.session.add(user)
        db.session.commit()
        log_register(user.username, user.email)

        flash('Registration successful. Please log in.', 'success')
        return redirect('/login.html')

    return redirect('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect('/dashboard.html')

    if request.method == 'POST':
        form       = request.form
        identifier = form.get('identifier', '').strip()
        password   = form.get('password', '')

        if '@' in identifier and is_valid_email(identifier):
            user = User.query.filter_by(email=identifier.lower()).first()
        else:
            username = sanitize_username(identifier)
            user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'error')
            log_login_failed(identifier)
            return redirect('/login.html')

        login_user(user)
        log_login_success(user.username)
        create_access_token(identity=user.user_id)
        flash('Logged in successfully. Redirecting to dashboard...', 'success')
        return redirect('/dashboard.html')

    return redirect('login.html')


@auth_bp.route('/login', methods=['GET'])
def login_page():
    return send_from_directory(FE, 'login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear Flask session data

    response = redirect('/login.html')
    response.delete_cookie('access_token_cookie')  # Adjust cookie name if different
    response.delete_cookie('csrf_token')  # If CSRF tokens are stored in cookies

    return response


