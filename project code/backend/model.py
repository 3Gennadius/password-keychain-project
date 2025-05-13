from flask_login import UserMixin
from backend import db
from .crypto import encrypt_master, decrypt_master
from .validation import sanitize_username

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.synonym('user_id')  # Flask-Login compatibility
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(95), unique=True, nullable=False)  # Changed to unique=True
    password_hash = db.Column(db.String(255), nullable=False)  # Changed length to 255
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    prefers_dark_mode = db.Column(db.Boolean, default=False)
    encrypted_master_password = db.Column(db.Text)  # Changed to Text to match DB schema
    avatar_path = db.Column(db.String(255), nullable=True)

    # Bcrypt-based login password hashing 
    def set_login_password(self, raw: str):
        """Hash the login password with bcrypt."""
        from flask_bcrypt import generate_password_hash
        self.password_hash = generate_password_hash(raw).decode('utf-8')

    def check_login_password(self, raw: str) -> bool:
        """Verify a raw password against the stored bcrypt hash."""
        from flask_bcrypt import check_password_hash
        return check_password_hash(self.password_hash, raw)

    def set_master_password(self, raw: str):
        self.encrypted_master_password = encrypt_master(raw)

    def get_master_password(self) -> str:
        return decrypt_master(self.encrypted_master_password or b'')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email
        }


class PasswordEntry(db.Model):
    __tablename__ = 'password_entries'

    entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    website = db.Column(db.LargeBinary, nullable=False)  # Directly named as in DB
    username = db.Column(db.LargeBinary, nullable=False)  # Directly named as in DB
    password = db.Column(db.LargeBinary, nullable=False)  # Directly named as in DB
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    # Relationship
    user = db.relationship('User', backref='password_entries')

    # Encryption/decryption methods
    def set_website(self, raw: str):
        self.website = encrypt_master(raw)

    def get_website(self) -> str:
        return decrypt_master(self.website)

    def set_username(self, raw: str):
        self.username = encrypt_master(raw)

    def get_username(self) -> str:
        return decrypt_master(self.username)

    def set_password(self, raw: str):
        self.password = encrypt_master(raw)

    def get_password(self) -> str:
        return decrypt_master(self.password)
    
    def to_dict(self):
        return {
            'entry_id': self.entry_id,
            'website': self.get_website(),
            'username': self.get_username(),
            'password': self.get_password(),
            'user_id': self.user_id
        }


