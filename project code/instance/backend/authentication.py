# backend/authentication.py

from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import create_access_token
from flask_bcrypt import generate_password_hash, check_password_hash
from backend.model import User
from backend.validation import sanitize_username, is_valid_email, is_strong_password
from backend import db, limiter, csrf

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def api_register():
    data = request.get_json() or request.form

    required_fields = [
        'first_name', 'last_name', 'date_of_birth',
        'username', 'email', 'password', 'confirm_password'
    ]
    for field in required_fields:
        if not data.get(field, '').strip():
            return jsonify(error=f"{field.replace('_', ' ').title()} is required."), 400

    username = sanitize_username(data['username'])
    if User.query.filter_by(username=username).first():
        return jsonify(error="Username already taken."), 409

    email = data['email'].strip()
    if not is_valid_email(email):
        return jsonify(error="Invalid email address."), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered."), 409

    pwd = data['password']
    if pwd != data['confirm_password']:
        return jsonify(error="Passwords do not match."), 400
    if not is_strong_password(pwd):
        return jsonify(error="Password is too weak."), 400

    hashed = generate_password_hash(pwd).decode('utf-8')
    new_user = User(
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        date_of_birth=data['date_of_birth'],
        username=username,
        email=email,
        password_hash=hashed
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(success=True, message="User registered successfully."), 201

@auth_bp.route('/api/login', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def api_login():
    data = request.get_json() or request.form
    ident = data.get('username', '').strip()
    password = data.get('password', '')

    if not ident or not password:
        return jsonify(error="Username (or email) and password required."), 400

    # determine whether ident is email or username
    if '@' in ident and is_valid_email(ident):
        user = User.query.filter_by(email=ident).first()
    else:
        user = User.query.filter_by(username=sanitize_username(ident)).first()

    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity=user.user_id)
        return jsonify(success=True, token=token), 200

    return jsonify(error="Invalid credentials."), 401

@auth_bp.route('/api/logout', methods=['POST'])
@csrf.exempt
def api_logout():
    # Stateless JWT—front end just drops the token
    return jsonify(success=True, message="Logged out successfully."), 200
