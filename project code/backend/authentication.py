import os
from flask import Blueprint, jsonify, request, redirect, redirect, flash, current_app, send_from_directory, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token
from . import db, csrf, limiter
from . import db 
from .model import User
from .validation import sanitize_username, is_valid_email, is_strong_password
from werkzeug.security import generate_password_hash, check_password_hash
from .logging_utils import log_login_failed, log_login_success, log_register

FE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/dashboard.html')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Simple validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect('/register.html')
        
        if password != confirm:
            flash('Passwords do not match', 'error')
            return redirect('/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect('/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect('/register.html')

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        # Log in the user
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect('/dashboard.html')
    
    # For GET requests, just serve the registration page
    return send_from_directory(FE, 'register.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/dashboard.html')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        flash('Invalid username or password', 'error')
        return redirect('/login.html')
    
    login_user(user)
    flash('Logged in successfully!', 'success')
    return redirect('/dashboard.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return send_from_directory('../frontend', 'login.html')


