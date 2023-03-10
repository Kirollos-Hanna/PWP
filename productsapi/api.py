from flask import Flask, Response, request, make_response
from flask_restful import Api, Resource
import json
from productsapi.db import db, User, Product, Product_categories, Review, Category
from sqlalchemy.exc import IntegrityError
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType
from productsapi.converters import UserConverter
from jsonschema import validate, ValidationError
from flask_caching import Cache

api = Api()

cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})

class UserItem(Resource):
    def get(self, user):
        cached_user = cache.get("user_"+str(user.id))
        if cached_user:
            return cached_user

        cache.set("user_"+str(user.id), user.serialize())
        return user.serialize()

    def put(self, user):
        print(type(request.headers))
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        user.deserialize(request.json)
        try:
            validate(user.serialize(), User.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))
        db.session.add(user)
        db.session.commit()
        cache.set("user_"+str(user.id), user.serialize())
        cache.delete("users_all")

        return Response(status=204)

    def delete(self, user):
        db.session.delete(user)
        db.session.commit()
        cache.delete("users_all")

        return Response(status=204)


class UserCollection(Resource):

    def get(self):
        cached_users = cache.get("users_all")
        if cached_users:
            return Response(headers={"Content-Type": "application/json"}, response=json.dumps(cached_users), status=200)
        users = User.query.all()
        users_json = []
        for user in users:
            users_json.append({
                'name': user.name,
                'password': user.password,
                'email': user.email,
                'role': user.role,
                'avatar': user.avatar,
                #'products': [product.serialize() for product in user.products],
                #'reviews': [review.serialize() for review in user.reviews]
            })
        cache.set("users_all", users_json)
        return Response(headers={"Content-Type": "application/json"}, response=json.dumps(users_json), status=200)

    def post(self):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        try:
            validate(request.json, User.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        user = User(
            name=request.json['name'],
            password=request.json['password'],
            email=request.json['email'],
            role=request.json['role'] if 'role' in request.json else "Customer",
            avatar=request.json['avatar'] if 'avatar' in request.json else None,
        )

        try:
            db.session.add(user)
            db.session.commit()
            cache.set("user_"+str(user.id), user.serialize())
        except IntegrityError:
            raise Conflict(
                description=f"User with name {request.json['name']} or email {request.json['email']} already exists"
            )
        cache.delete("users_all")

        response = make_response()
        api_url = api.url_for(UserItem, user=user)
        response.headers['location'] = api_url
        response.status_code = 201
        return response


class ProductItem(Resource):

    def get(self, product):
        cached_product = cache.get("product_"+str(product.id))
        if cached_product:
            return cached_product

        cache.set("product_"+str(product.id), product.serialize())
        return product.serialize()

    def put(self, product):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        try:
            product.deserialize(request.json)

            user = None
            if 'user_name' in request.json:
                try:
                    user = User.query.filter_by(
                        name=request.json['user_name']).first()
                    if user:
                        product.user = user
                except (IntegrityError, KeyError) as e_i:
                    raise BadRequest

            categories = None
            if 'categories' in request.json:
                categories = Category.query.filter(
                    Category.name.in_(request.json['categories'])).all()
                if categories:
                    product.categories = categories
                else:
                    raise BadRequest

            try:
                validate(request.json,
                         Product.json_schema(is_updating=True))
            except ValidationError as e_v:
                raise BadRequest(description=str(e_v))

            db.session.commit()
            cache.set("product_"+str(product.id), product.serialize())
            cache.delete("products_all")

        except IntegrityError:
            raise Conflict(
                description="Product with name already exists."
            )
        return Response(status=204)

    def delete(self, product):
        db.session.delete(product)
        db.session.commit()
        cache.delete("products_all")

        return Response(status=204)


class ProductCollection(Resource):

    def get(self):
        cached_products = cache.get("products_all")
        if cached_products:
            return Response(headers={"Content-Type": "application/json"}, response=json.dumps(cached_products), status=200)
        products = Product.query.all()
        products_json = []
        for product in products:
            products_json.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'images': json.loads(product.images) if product.images else None,
                'user_name': product.user_name,
                'reviews': [review.serialize(include_product=False) for review in product.reviews],
                'categories': [category.serialize(long=False) for category in product.categories],
            })
        cache.set("products_all", products_json)
        return Response(headers={"Content-Type": "application/json"}, response=json.dumps(products_json), status=200)

    def post(self):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        try:
            validate(request.json, Product.json_schema(is_updating=False))
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        user = User.query.filter_by(
            name=request.json['user_name']).first()

        categories = None
        if 'categories' in request.json:
            categories = Category.query.filter(
                Category.name.in_(request.json['categories'])).all()

        try:
            product = Product(
                name=request.json['name'],
                price=request.json['price'],
                description=request.json['description'] if 'description' in request.json else None,
                images=json.dumps(
                    request.json['images']) if 'images' in request.json else None,
                user=user
            )
            if categories:
                product.categories = categories

            db.session.add(product)
            db.session.commit()
            cache.set("product_"+str(product.id), product.serialize())

        except IntegrityError as e_i:
            raise Conflict(
                description=e_i
            )

        cache.delete("products_all")
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
       #         description=f'Failed to link product: {request.json["name"]} to category: {request.json["category"]}'
       #     )

        response = make_response()
        api_url = api.url_for(ProductItem, product=product)
        response.headers['location'] = api_url
        response.status_code = 201
        return response


class ReviewItem(Resource):

    def get(self, review):
        cached_review = cache.get("review_"+str(review.id))
        if cached_review:
            return cached_review

        cache.set("review_"+str(review.id), review.serialize())
        return review.serialize()

    def put(self, review):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        review.deserialize(request.json)

        if 'user_name' in request.json:
            raise BadRequest(description="Cannot update user name")

        if 'product_name' in request.json:
            raise BadRequest(description="Cannot update product name")

        review.deserialize(request.json)

        db.session.add(review)
        db.session.commit()
        cache.set("review_"+str(review.id), review.serialize())
        cache.delete("reviews_all")

        return Response(status=204)

    def delete(self, review):
        db.session.delete(review)
        db.session.commit()
        cache.delete("reviews_all")

        return Response(status=204)


class ReviewCollection(Resource):

    def get(self):
        cached_reviews = cache.get("reviews_all")
        if cached_reviews:
            return Response(headers={"Content-Type": "application/json"}, response=json.dumps(cached_reviews), status=200)
        reviews = Review.query.all()
        reviews_json = []

        for review in reviews:
            reviews_json.append({
                'id': review.id,
                'description': review.description,
                'rating': review.rating,
                'user_name': review.user_name,
                'product_name': review.product_name,
                #'user': review.user.serialize(),
                #'product': review.product.serialize(),
            })
        cache.set("reviews_all", reviews_json)
        return Response(headers={"Content-Type": "application/json"}, response=json.dumps(reviews_json), status=200)

    def post(self):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        try:
            validate(request.json, Review.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        user = User.query.filter_by(
            name=request.json['user_name']).first()
        product = Product.query.filter_by(
            name=request.json['product_name']).first()
        if user is None or product is None:
            return Response("User or product not found in the db", status=409)

        try:
            review = Review(
                description=request.json['description'] if 'description' in request.json else None,
                rating=request.json['rating'],
                user=user,
                product=product
            )
        except (ValueError, KeyError, IntegrityError) as e_v:
            return Response(response=str(e_v), status=400)

        db.session.add(review)
        db.session.commit()
        cache.set("review_"+str(review.id), review.serialize())
        cache.delete("reviews_all")

        response = make_response()
        api_url = api.url_for(ReviewItem, review=review)
        response.headers['location'] = api_url
        response.status_code = 201
        return response


class CategoryItem(Resource):

    def get(self, category):
        cached_category = cache.get("category_"+str(category.id))
        if cached_category:
            return cached_category

        cache.set("category_"+str(category.id), category.serialize())
        return category.serialize()

    def put(self, category):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        try:
            validate(request.json, Category.json_schema(is_updating=True))
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        category.deserialize(request.json)

        if 'product_names' in request.json:
            products = Product.query.filter(
                Product.name.in_(request.json['product_names'])).all()
            if not products:
                raise BadRequest(description="Product names do not exist")
            else:
                category.products = products

        db.session.add(category)
        db.session.commit()
        cache.set("category_"+str(category.id), category.serialize())
        cache.delete("categories_all")

        return Response(status=204)

    def delete(self, category):
        db.session.delete(category)
        db.session.commit()
        cache.delete("categories_all")

        return Response(status=204)


class CategoryCollection(Resource):

    def get(self):
        cached_categories = cache.get("categories_all")
        if cached_categories:
            return Response(headers={"Content-Type": "application/json"}, response=json.dumps(cached_categories), status=200)
        categories = Category.query.all()
        category_json = []
        for category in categories:
            category_json.append({
                'id': category.id,
                'name': category.name,
                'image': category.image,
                # 'products': [product.serialize(long=False) for product in category.products]
            })
        cache.set("categories_all", category_json)
        return Response(headers={"Content-Type": "application/json"}, response=json.dumps(category_json), status=200)

    def post(self):
        if request.content_type != 'application/json':
            raise UnsupportedMediaType

        try:
            validate(request.json, Category.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        products = None
        if 'product_names' in request.json:
            products = Product.query.filter(
                Product.name.in_(request.json['product_names'])).all()
            if not products:
                raise BadRequest(description="Product names do not exist")

        try:
            category = Category(
                name=request.json['name'],
                image=request.json['image'] if 'image' in request.json else None
            )
            if products:
                category.products = products
            db.session.add(category)
            db.session.commit()
            cache.set("category_"+str(category.id), category.serialize())

        except (IntegrityError) as e_v:
            return Response("Category already exists", 409)

        cache.delete("categories_all")

        response = make_response()
        api_url = api.url_for(CategoryItem, category=category)
        response.headers['location'] = api_url
        response.status_code = 201
        return response

# Routing resources


api.add_resource(UserItem, "/api/users/<user:user>/")
api.add_resource(UserCollection, "/api/users/")

api.add_resource(ProductItem, "/api/products/<product:product>/")
api.add_resource(ProductCollection, "/api/products/")

api.add_resource(ReviewItem, "/api/reviews/<review:review>/")
api.add_resource(ReviewCollection, "/api/reviews/")

api.add_resource(CategoryItem, "/api/categories/<category:category>/")
api.add_resource(CategoryCollection, "/api/categories/")