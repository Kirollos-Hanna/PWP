from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from db import db
from api import api 
from converters import UserConverter, ProductConverter, ReviewConverter, CategoryConverter

#Create Flask app with proper parameters
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Create db using SQLAlchemy
db.init_app(app)

# Map converters
app.url_map.converters['user'] = UserConverter 
app.url_map.converters['product'] = ProductConverter 
app.url_map.converters['review'] = ReviewConverter 
app.url_map.converters['category'] = CategoryConverter 

# Init api
api.init_app(app)

#Setup the sqlite db to use foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
