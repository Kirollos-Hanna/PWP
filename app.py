from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class User(db.Model):
    avatar=db.Column(db.String(256), nullable=True)
    email=db.Column(db.String(256), nullable=False)
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(256), nullable=False)
    password=db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(256), nullable=True)

class Review(db.Model):
    description = db.Column(db.String(256), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), unique=True)

class Product(db.Model):
    description = db.Column(db.String(256), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    images = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(256), nullable=False)

class Product_categories(db.Model):
    product_category_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), unique=True)