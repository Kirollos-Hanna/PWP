from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Create Flask app with proper parameters
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Create db using SQLAlchemy
db = SQLAlchemy(app)

#Setup the sqlite db to use foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

#Create table for many-to-many relationship between categories and products
product_categories = db.Table("product_categories",
       db.Column("product_id", db.Integer, db.ForeignKey("product.id"), primary_key=True),             
       db.Column("category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True)             
)

class User(db.Model):
    avatar=db.Column(db.String(256), nullable=True)
    email=db.Column(db.String(256), nullable=False)
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(256), nullable=False)
    password=db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(256), nullable=True)

    products = db.relationship("Product", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")

class Review(db.Model):
    description = db.Column(db.String(65535), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")

class Product(db.Model):
    description = db.Column(db.String(65535), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    images = db.Column(db.String(65535), nullable=True)
    name = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship("User", back_populates="products")
    reviews = db.relationship("Review", back_populates="product")
    categories = db.relationship("Category", secondary=product_categories, back_populates="products")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(256), nullable=False)

    products = db.relationship("Product", secondary=product_categories, back_populates="categories")
