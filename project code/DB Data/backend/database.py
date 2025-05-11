from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

def init_app(app):
    database.init_app(app)
