from flask import Flask, Response, request, make_response
from flask_restful import Api, Resource
import json 
from db import db, User, Product, Product_categories, Review, Category
from sqlalchemy.exc import IntegrityError
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType
from converters import UserConverter

api = Api()

class DeleteAll(Resource):

    def delete_and_commit(self, value):
        db.session.delete(value)
        db.session.commit()

    def get(self):
        users = [self.delete_and_commit(user) for user in User.query.all()]
        product = [self.delete_and_commit(prod) for prod in Product.query.all()]
        review = [self.delete_and_commit(review) for review in Review.query.all()]
        category = [self.delete_and_commit(category) for category in Category.query.all()]

class UserItem(Resource):
    def get(self, user):
        return user.serialize()

    def put(self, user):
        if not request.json:
            raise UnsupportedMediaType
        
        user.deserialize(request.json)
            
        try:
            db.session.add(user)
            db.session.commit()
            
           
        except IntegrityError:
           raise Conflict(
                409,
                description="User with name already exists."
                
            )
        return Response(status=204)

class UserCollection(Resource):

    def get(self):
        users = User.query.all()
        users_json = []
        for user in users:
            users_json.append({
                'username': user.username,
                'password': user.password,
                'email': user.email,
                'avatar': user.avatar,
                'products': [product.serialize() for product in user.products],
                'reviews': [review.serialize() for review in user.reviews]
            })

        return Response(json.dumps(users_json), status=200)
        
    def post(self):
        if not request.json:
            raise UnsupportedMediaType

        # TODO:: implement User.json_schema() 
        # try:
        #     validate(request.json, User.json_schema())
        # except ValidationError as e_v:
        #     raise BadRequest(description=str(e_v))

        try:
            user = User(
                username=request.json['username'],
                password=request.json['password'],
                email=request.json['email'],
                role=request.json['role'],
                avatar=request.json['avatar'],
                )
        except (ValueError, KeyError) as e_v:
            return Response("Failed to parse request.json", 400)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                409,
                description=f"User with name {request.json['username']} already exists"
            )

        response = make_response()
        api_url = api.url_for(UserItem, user=user)
        response.headers['location'] = api_url
        response.status_code = 201
        return response


class ProductItem(Resource):

    def get(self, product):
        return product.serialize()
    
    def put(self, product):
        if not request.json:
            raise UnsupportedMediaType
        
        product.deserialize(request.json)
            
        try:
            db.session.add(product)
            db.session.commit()
            
           
        except IntegrityError:
           raise Conflict(
                409,
                description="Product with name name already exists."
                
            )
        return Response(status=204)

class ProductCollection(Resource):

    def get(self):
        products = Product.query.all()
        products_json = []
        # TODO:: Verify if we need all these values ?
        for product in products:
            print(type(product.user))
            products_json.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'images': product.images,
                'user_id': product.user_id,
                'user': None if type(product.user) == type(None) else product.user.serialize(),
                'reviews': [review.serialize() for review in product.reviews],
                'category': [category.serialize() for category in product.categories],
            })
        return Response(json.dumps(products_json), status=200)

    def post(self):
        if not request.json:
            raise UnsupportedMediaType

        # TODO:: implement Product.json_schema() 
        # try:
        #     validate(request.json, Product.json_schema())
        # except ValidationError as e_v:
        #     raise BadRequest(description=str(e_v))

        # TODO:: Is this correct implementation?
        # Try to find the user from the db, if user is not found
        # mark it as None (Every product doesn't need user?)
        try:
            user=User.query.filter_by(username=request.json['username']).first()
        except IntegrityError as e_i:
            print("User not found in the db")
            user = None
        except KeyError as e_k:
            print("No username defined in response.json")
            user = None
    

        try:
            product = Product(
                name=request.json['name'],
                price=request.json['price'],
                description=request.json['description'],
                images=request.json['images'],
                user=user
                )
                
            if not Product.query.filter_by(name=request.json['name']).first() == None:
                return "Product with this handle already exists", 409
                
            db.session.add(product)
            db.session.commit()
                
        except IntegrityError:
            raise Conflict(
                409,
                description=f"Product with name {request.json['name']} already exists"
            )        
        except (ValueError, KeyError) as e_v:
            return Response("Failed to parse request.json", 400)
        
        
       
        
       # NOTE:: CAN BE OF USE WHEN LINKING PRODUCTS TO CATEGORIES
       # WHEN CREATING PRODUCTS, CREATES CATEGORIES IF THEY ARE NOT YET CREATED
       # try: 
       #     cats = Category.query.filter(Category.name.in_(request.json['categories'])).all()

       #     # If the categories were not found in db, create them first
       #     if cats is []:
       #         for cat_name in request.json['categories']:
       #             cat = Category(name=cat_name)
       #             cats.append(cat.id)
       #             db.session.add(cat)
       #             db.commit()

       #     # Add the relationships between every product-category
       #     for cat in cats:
       #         print(cat)
       #         prod_cat = Product_categories(product_id=product.id, category_id=cat.id)
       #         db.session.add(prod_cat)
       #         db.commit()

       # except IntegrityError as e_v:
       #     raise Conflict(
       #         409,
       #         description=f'Failed to link product: {request.json["name"]} to category: {request.json["category"]}'
       #     )

        response = make_response()
        api_url = api.url_for(ProductItem, product=product)
        response.headers['location'] = api_url
        response.status_code = 201
        return response

class ReviewItem(Resource):

    def get(self, review):
        return review.serialize()
        
    def put(self, review):
        if not request.json:
            raise UnsupportedMediaType
        
        review.deserialize(request.json)
            
        
        db.session.add(review)
        db.session.commit()
            
        return Response(status=204)

class ReviewCollection(Resource):

    def get(self):
        reviews = Review.query.all()
        reviews_json = []
        # TODO:: Verify if we need all these values ?
        for review in reviews:
            reviews_json.append({
                'id': review.id,
                'description': review.description,
                'rating': review.rating,
                'user_id': review.user_id,
                'product_id': review.product.id,
                'user': review.user.serialize(),
                'product': review.product.serialize(),
            })

        return Response(json.dumps(reviews_json), status=200)

    def post(self):
        if not request.json:
            raise UnsupportedMediaType

        # TODO:: implement Product.json_schema() 
        # try:
        #     validate(request.json, Product.json_schema())
        # except ValidationError as e_v:
        #     raise BadRequest(description=str(e_v))

        # TODO:: Is this correct implementation?
        try:
            user = User.query.filter_by(username=request.json['username']).first()
            product = Product.query.filter_by(name=request.json['product_name']).first()
            if user is None or product is None:
                return Response("User or product not found in the db", status=409)
        except IntegrityError as e_v:
            return Response("User or product not found in the db", status=409)
        except KeyError as e_k:
            print("No username or product_name defined in response.json")

        try:
            review = Review(
                description=request.json['description'],
                rating=request.json['rating'],
                user_id=user.id,
                product_id=product.id,
                user=user,
                product=product
                )
        except (ValueError, KeyError, IntegrityError) as e_v:
            return Response("Failed to parse request.json", 400)

        db.session.add(review)
        db.session.commit()

        response = make_response()
        api_url = api.url_for(ReviewItem, review=review)
        response.headers['location'] = api_url
        response.status_code = 201
        return response


class CategoryItem(Resource):

    def get(self, category):
        return category.serialize()
        
    def put(self, cat):
        if not request.json:
            raise UnsupportedMediaType
        
        cat.deserialize(request.json)
            
        
        db.session.add(cat)
        db.session.commit()
            
        return Response(status=204)

class CategoryCollection(Resource):

    def get(self):
        categories = Category.query.all()
        category_json = []
        # TODO:: Verify if we need all these values ?
        for category in categories:
            category_json.append({
                'id': category.id,
                'name': category.name,
                'image': category.image,
                'products': [product.serialize() for product in category.products]
            })

        return Response(json.dumps(category_json), status=200)

    def post(self):
        if not request.json:
            raise UnsupportedMediaType

        # TODO:: implement Category.json_schema() 
        # try:
        #     validate(request.json, Category.json_schema())
        # except ValidationError as e_v:
        #     raise BadRequest(description=str(e_v))

        # TODO:: Is this correct implementation?
        try:
            products = Product.query.filter(Product.categories.any(name=request.json['name']))
            if products is None:
                products = []
        except IntegrityError as e_v:
            return Response("Products not found in the db", status=409)

        try:
            category = Category(
                name=request.json['name'],
                image=request.json['image'],
                products=list(products)
                )
        except (ValueError, KeyError, IntegrityError) as e_v:
            return Response("Failed to parse request.json", 400)

        db.session.add(category)
        db.session.commit()

        response = make_response()
        api_url = api.url_for(CategoryItem, category=category)
        response.headers['location'] = api_url
        response.status_code = 201
        return response

api.add_resource(UserItem, "/api/users/<user:user>/")
api.add_resource(UserCollection, "/api/users/")

api.add_resource(ProductItem, "/api/products/<product:product>/")
api.add_resource(ProductCollection, "/api/products/")

api.add_resource(ReviewItem, "/api/reviews/<review:review>/")
api.add_resource(ReviewCollection, "/api/reviews/")

api.add_resource(CategoryItem, "/api/categories/<category:category>/")
api.add_resource(CategoryCollection, "/api/categories/")

# For testing purposes
api.add_resource(DeleteAll, "/api/DROP_TABLE_ALL")
