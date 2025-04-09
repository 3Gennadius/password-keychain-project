import os
import base64
from flask_login import UserMixin
from backend.database import database
from cryptography.fernet import Fernet

#Load AES key
AES_KEY = os.getenv("AES_KEY")
if not AES_KEY:
    raise ValueError("AES KEY MISSING")

cipher = Fernet(AES_KEY)

class User(UserMixin, database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(180), unique=True, nullable=False)
    password_encrypted = database.Column(database.Text, nullable=False)  

    """Encrypt password"""
    def set_password(self, password):      
        encrypted_password = cipher.encrypt(password.encode())
        self.password_encrypted = base64.b64encode(encrypted_password).decode()

    """Decrypt and compare with input"""
    def check_password(self, password):
        try:
            decrypted_password = cipher.decrypt(base64.b64decode(self.password_encrypted)).decode()
            return decrypted_password == password
        except Exception:
            return False 