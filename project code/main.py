# File: main.py

import os
from dotenv import load_dotenv
from datetime import timedelta
from flask import Flask, send_from_directory, redirect
from flask_login import current_user
from flask_jwt_extended import JWTManager

from backend import create_app, db, login_manager
from backend.model import User

# Load environment variables
load_dotenv()

# Create app and initialize JWT
app = create_app()
jwt = JWTManager(app)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Register user_loader on the shared login_manager
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Static and protected routes
BASE = os.path.dirname(os.path.abspath(__file__))
FE = os.path.join(BASE, 'frontend')

@app.route('/')
def index():
    return send_from_directory(FE, 'index.html')

@app.route('/login.html')
def login_page():
    if current_user.is_authenticated:
        return redirect('/dashboard.html')
    return send_from_directory(FE, 'login.html')

@app.route('/register.html')
def register_page():
    if current_user.is_authenticated:
        return redirect('/dashboard.html')
    return send_from_directory(FE, 'register.html')

@app.route('/dashboard.html')
def dashboard_page():
    if not current_user.is_authenticated:
        return redirect('/login.html')
    return send_from_directory(FE, 'dashboard.html')

@app.route('/manage-passwords.html')
def manage_passwords_page():
    if not current_user.is_authenticated:
        return redirect('/login.html')
    return send_from_directory(FE, 'manage-passwords.html')

@app.route('/profile.html')
def profile_page():
    if not current_user.is_authenticated:
        return redirect('/login.html')
    return send_from_directory(FE, 'profile.html')

@app.route('/logout.html')
def logout_page():
    if not current_user.is_authenticated:
        return redirect('/login.html')
    return send_from_directory(FE, 'logout.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FE, filename)


if __name__ == '__main__':
    app.run(debug=True)
