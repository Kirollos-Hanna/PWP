from flask_sqlalchemy import SQLAlchemy
import enum
import json

db = SQLAlchemy()

# Create table for many-to-many relationship between categories and products
Product_categories = db.Table("product_categories",
                              db.Column("product_id", db.Integer, db.ForeignKey(
                                  "product.id"), primary_key=True),
                              db.Column("category_id", db.Integer, db.ForeignKey(
                                  "category.id"), primary_key=True)
                              )


class RoleType(str, enum.Enum):
    Customer = "Customer"
    Admin = "Admin"
    Seller = "Seller"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    role = db.Column(db.Enum(RoleType), nullable=False)
    avatar = db.Column(db.String(256), nullable=True)

    products = db.relationship("Product", back_populates="user")
    reviews = db.relationship("Review", back_populates="user")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "role", "password", "email"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "The user's name",
            "type": "string",
            "minLength": 1,
            "maxLength": 256
        }
        props["role"] = {
            "description": "The user's role",
            "type": "string",
            "enum": ["Customer", "Admin", "Seller"],
            "default": "Customer"
        }
        props["password"] = {
            "description": "User password",
            "type": "string",
            "minLength": 6,
            "maxLength": 256
        }
        props["email"] = {
            "description": "User email",
            "type": "string",
            "format": "email",
            "minLength": 1,
            "maxLength": 256
        }
        props["avatar"] = {
            "description": "The url of the user's avatar",
            "type": ["string", "null"],
            "format": "uri",
            "pattern": "^https?://",
            "minLength": 1,
            "maxLength": 256
        }
        return schema

    def serialize(self, long=True):
        serialized_user = {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar
        }

        if long:
            serialized_user["products"] = [product.serialize(
                long=False) for product in self.products]
            serialized_user["reviews"] = [review.serialize(
                include_user=False) for review in self.reviews]

        return serialized_user

    def deserialize(self, doc):
        self.name = doc['name'] if 'name' in doc else self.name
        self.password = doc['password'] if 'password' in doc else self.password
        self.email = doc['email'] if 'email' in doc else self.email
        self.role = doc['role'] if 'role' in doc else self.role
        self.avatar = doc['avatar'] if 'avatar' in doc else self.avatar
        #self.products = doc['products'] if 'products' in doc else self.products
        #self.reviews = doc['reviews'] if 'reviews' in doc else self.reviews


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(65535), nullable=True)
    rating = db.Column(db.Float, nullable=False)

    user_name = db.Column(db.String(256), db.ForeignKey("user.name"), nullable=False)
    product_name = db.Column(db.String(256), db.ForeignKey(
        "product.name"), nullable=False)

    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["rating", "product_name", "user_name"]
        }

        props = schema["properties"] = {}

        props["rating"] = {
            "description": "The rating of the product by a user from 1 to 10",
            "type": "number",
            "minimum": 1,
            "maximum": 10,
        }

        props["user_name"] = {
            "description": "The username of the reviewer",
            "type": "string",
            "minLength": 1,
            "maxLength": 256
        }

        props["product_name"] = {
            "description": "The product name being reviewed",
            "type": "string",
            "minLength": 1,
            "maxLength": 256
        }

        return schema

    def serialize(self, include_product=True, include_user=True):
        serialized_review = {
            'id': self.id,
            'user_name': self.user_name,
            'description': self.description,
            'rating': self.rating,
            'product_name': self.product_name
        }
        
        if include_product or include_user:
            serialized_review.pop("product_name")
            serialized_review.pop("user_name")

        if include_user:
            serialized_review['user'] = self.user.serialize(long=False)

        if include_product:
            serialized_review['product'] = self.product.serialize(long=False)

        return serialized_review

    def deserialize(self, doc):
        self.id = doc['id'] if 'id' in doc else self.id
        self.rating = doc['rating'] if 'rating' in doc else self.rating
        self.description = doc['description'] if 'description' in doc else self.description
        self.user_name = doc['user_name'] if 'user_name' in doc else self.user_name
        self.product_name = doc['product_name'] if 'product_name' in doc else self.product_name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(65535), nullable=True)
    images = db.Column(db.String(65535), nullable=True)
    user_name = db.Column(db.String(256), db.ForeignKey("user.name"), nullable=False)
    #user_name = db.Column(db.String(256), nullable=False)

    user = db.relationship("User", back_populates="products")
    reviews = db.relationship("Review", back_populates="product")
    categories = db.relationship(
        "Category", secondary=Product_categories, back_populates="products")

    @staticmethod
    def json_schema(is_updating):
        schema = {
            "type": "object",
            "required": ["name", "price", "user_name"]
        }

        if is_updating:
            schema = {
                "type": "object",
            }

        props = schema["properties"] = {}

        props["user_name"] = {
            "description": "The user id of the user who created this product",
            "type": "string",
            "minLength": 1,
            "maxLength": 256
        }

        props["name"] = {
            "description": "Product Name",
            "type": "string",
            "minLength": 1,
            "maxLength": 256
        }

        props["price"] = {
            "description": "Product Price",
            "type": "number",
            "minimum": 1,
            "maximum": 100000
        }

        props["description"] = {
            "description": "Product description",
            "type": "string",
            "minLength": 1,
            "maxLength": 65535
        }

        props["images"] = {
            "description": "A list of product image urls",
            "type": ["array", "null"],
            "items": {
                "type": "string",
                "format": "uri",
                "pattern": "^https?://",
                "minLength": 1,
                "maxLength": 256
            },
            "maxItems": 255
        }

        props["categories"] = {
            "description": "An array of category names that this product belongs to",
            "type": ["array", "null"],
            "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": 256
            },
            "maxItems": 255
        }

        return schema

    def serialize(self, long=True):
        serialized_product = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'images': json.loads(self.images) if self.images else None
        }

        if long:
            serialized_product["categories"] = [category.serialize(
                long=False) for category in self.categories]
            serialized_product["reviews"] = [review.serialize(
                include_product=False) for review in self.reviews]

        return serialized_product

    def deserialize(self, doc):
        self.id = doc['id'] if 'id' in doc else self.id
        self.name = doc['name'] if 'name' in doc else self.name
        self.price = doc['price'] if 'price' in doc else self.price
        self.description = doc['description'] if 'description' in doc else self.description
        self.images = json.dumps(doc['images']) if 'images' in doc else self.images
        self.user_name = doc['user_name'] if 'user_name' in doc else self.user_name
        #self.reviews = doc['reviews'] if 'reviews' in doc else self.reviews
        #self.categories = doc['categories'] if 'categories' in doc else self.categories


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(256), nullable=False, unique=True)

    products = db.relationship(
        "Product", secondary=Product_categories, back_populates="categories")

    @staticmethod
    def json_schema(is_updating=False):
        schema = {
            "type": "object",
            "required": ["name"]
        }
        
        if is_updating:
            schema = {
                "type": "object",
            }
            
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Category name",
            "type": "string",
            "minLength": 1,
            "maxLength": 256
        }
        props["image"] = {
            "description": "A url for an image related to the category",
            "type": ["string", "null"],
            "format": "uri",
            "pattern": "^https?://",
            "minLength": 1,
            "maxLength": 256
        }

        props["product_names"] = {
            "description": "A list of product names related to the category",
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": 256
            },
        }
        return schema

    def serialize(self, long=True):
        serialized_category = {
            'id': self.id,
            'name': self.name,
            'image': self.image,
        }

        if long:
            serialized_category["products"] = [
                product.serialize(long=False) for product in self.products]

        return serialized_category

    def deserialize(self, doc):
        self.id = doc['id'] if 'id' in doc else self.id
        self.name = doc['name'] if 'name' in doc else self.name
        self.image = doc['image'] if 'image' in doc else self.image
