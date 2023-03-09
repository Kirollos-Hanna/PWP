from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy import event
from productsapi.db import db
from productsapi.api import api, cache
from productsapi.converters import UserConverter, ProductConverter, ReviewConverter, CategoryConverter
import os

# Setup the sqlite db to use foreign keys

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///test.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    
    # Map converters
    app.url_map.converters['user'] = UserConverter
    app.url_map.converters['product'] = ProductConverter
    app.url_map.converters['review'] = ReviewConverter
    app.url_map.converters['category'] = CategoryConverter

    # Init api
    api.init_app(app)

    # Init cache
    cache.init_app(app)
    return app