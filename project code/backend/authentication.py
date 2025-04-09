from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
from backend.model import User, database

#Creating blueprint and routes
auth_bp = Blueprint('authentification', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register the user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already in use'}), 400

    user = User(username=username)
    user.set_password(password)
    database.session.add(user)
    database.session.commit()    

    return jsonify({'message': 'Account registered'}), 201

#Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid username and or password'}), 401

#Logout
@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out '}), 200