from flask_sqlalchemy import SQLAlchemy

#Creating database object
database = SQLAlchemy()

def init_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.database'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    database.init_app(app)