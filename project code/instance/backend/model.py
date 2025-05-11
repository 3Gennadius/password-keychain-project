# backend/model.py

from flask_login import UserMixin
from backend import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # Primary key
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.synonym('user_id')  # for Flask-Login

    username = db.Column(db.String(45), unique=True, nullable=False)
    email    = db.Column(db.String(95), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Optional profile fields
    first_name    = db.Column(db.String(100))
    last_name     = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)

    # Reversible master password
    encrypted_master_password = db.Column(db.Text)

    # Avatar path
    profile_image = db.Column(db.String(255))

    def set_login_password(self, raw: str):
        from flask_bcrypt import generate_password_hash
        self.password_hash = generate_password_hash(raw).decode('utf-8')

    def check_login_password(self, raw: str) -> bool:
        from flask_bcrypt import check_password_hash
        return check_password_hash(self.password_hash, raw)

    def set_master_password(self, raw: str):
        from .crypto import encrypt_master
        self.encrypted_master_password = encrypt_master(raw)

    def get_master_password(self) -> str:
        from .crypto import decrypt_master
        return decrypt_master(self.encrypted_master_password or "")


class PasswordEntry(db.Model):
    __tablename__ = 'password_entries'

    entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id       = db.synonym('entry_id')

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )

    label     = db.Column(db.String(255), nullable=False)
    _username = db.Column('username', db.Text, nullable=False)
    _password = db.Column('password', db.Text, nullable=False)

    def set_username(self, raw: str):
        self._username = raw

    def get_username(self) -> str:
        return self._username

    def set_password(self, raw: str):
        from .crypto import encrypt_master as encrypt_data
        self._password = encrypt_data(raw)

    def get_password(self) -> str:
        from .crypto import decrypt_master as decrypt_data
        return decrypt_data(self._password)
