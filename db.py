from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

db = SQLAlchemy()

#Create table for many-to-many relationship between categories and products
Product_categories = db.Table("product_categories",
       db.Column("product_id", db.Integer, db.ForeignKey("product.id"), primary_key=True),             
       db.Column("category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True)             
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(256), nullable=False)
    password=db.Column(db.String(256), nullable=False)
    email=db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(256), nullable=True)
    avatar=db.Column(db.String(256), nullable=True)

    products = db.relationship("Product", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")

    def serialize(self):
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
        }

    def deserialize(self, doc):
        self.username = doc['username']
        self.password = doc['password']
        self.email= doc['email']
        self.role= doc.get('role')
        self.avatar = doc.get('avatar')
        #self.products = doc.get('products')
        #self.reviews = doc.get('reviews')
            

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(65535), nullable=True)
    rating = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")

    def serialize(self):
        return {
            'username': self.user.username,
            'description': self.description,
            'rating': self.rating,
        }
        
    def deserialize(self, doc):
        self.description = doc['description']
        self.rating = doc.get('rating')
        

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(65535), nullable=True)
    images = db.Column(db.String(65535), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    user = db.relationship("User", back_populates="products")
    reviews = db.relationship("Review", back_populates="product")
    categories = db.relationship("Category", secondary=Product_categories, back_populates="products")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'images': self.images,
        }

    def deserialize(self, doc):
        #self.id = doc.get('id')
        self.name = doc['name']
        self.price = doc['price']
        self.description = doc.get('description')
        self.images = doc.get('images')
        self.user_id = doc.get('user_id')
        #self.user = doc.get('user')
        #self.reviews = doc.get('reviews')
        #self.categories = doc.get('categories')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(256), nullable=False)

    products = db.relationship("Product", secondary=Product_categories, back_populates="categories")

    def serialize(self):
        return {
            'name': self.name,
            'image': self.image,
        }
        
    def deserialize(self, doc):
        self.image = doc.get('image')
        self.name = doc['name']
