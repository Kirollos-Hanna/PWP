import json
from flask import Response, request, make_response, jsonify, url_for
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from jsonschema import validate, ValidationError
from flask_caching import Cache
from productsapi.db import db, User, Product, Review, Category, BlacklistToken
from validate_email import validate_email
#from werkzeug.routing import BaseConverter
#from productsapi.converters import UserConverter
api = Api()

cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})

MASON = "application/vnd.mason+json"
ERROR_PROFILE = "/profiles/error/"
LINK_RELATIONS_URL = "/commercemeta/link-relations#"

USER_PROFILE_URL = "/profiles/user/"
PRODUCT_PROFILE_URL = "/profiles/product/"
CATEGORY_PROFILE_URL = "/profiles/category/"
REVIEW_PROFILE_URL = "/profiles/review/"

# HELPER FUNCTIONS

def authorizeUser(auth_header):
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            responseObject = {
                'status': 'fail',
                'message': 'Bearer token malformed.'
            }
            response = jsonify(responseObject)
            response.status_code = 401
            return response
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if 'token blacklisted' in resp.lower() or 'signature expired' in resp.lower() or 'invalid token' in resp.lower():
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            response = jsonify(responseObject)
            response.status_code = 401
            return response
        else:
            
            return "authorized"
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        response = jsonify(responseObject)
        response.status_code = 401
        return response
    

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    def add_control_post(self, ctrl_name, title, href, schema):
        """
        Utility method for adding POST type controls. The control is
        constructed from the method's parameters. Method and encoding are
        fixed to "POST" and "json" respectively.
        
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """
    
        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_put(self, title, href, schema):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control name, method and
        encoding are fixed to "edit", "PUT" and "json" respectively.
        
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            "edit",
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema
        )
        
    def add_control_delete(self, title, href):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control method is fixed to
        "DELETE", and control's name is read from the class attribute
        *DELETE_RELATION* which needs to be overridden by the child class.

        : param str href: target URI for the control
        : param str title: human-readable title for the control
        """
        
        self.add_control(
            "commercemeta:delete",
            href,
            method="DELETE",
            title=title,
        )

class CommerceMetaBuilder(MasonBuilder):
    def add_control_users_all(self):
        self.add_control(
            "commercemeta:users-all",
            api.url_for(UserCollection),
            title ="all users"
        )

    def add_control_products_all(self):
        self.add_control(
            "commercemeta:products-all",
            url_for("products"),
            title ="all products"
        )

    def add_control_categories_all(self):
        self.add_control(
            "commercemeta:categories-all",
            url_for("categories"),
            title ="all categories"
        )
    
    def add_control_reviews_all(self):
        self.add_control(
            "commercemeta:reviews-all",
            url_for("reviews"),
            title ="all reviews"
        )

    def add_control_users_add(self):
        self.add_control_post(
            "commercemeta:add-user",
            title ="add new user",
            href=api.url_for(UserCollection),
            schema=User.json_schema()
        )

    def add_control_products_add(self):
        self.add_control_post(
            "commercemeta:add-product",
            title ="add new product",
            href=api.url_for(ProductCollection),
            schema=Product.json_schema()
        )

    def add_control_categories_add(self):
        self.add_control_post(
            "commercemeta:add-category",
            title ="add new category",
            href=api.url_for(CategoryCollection),
            schema=Category.json_schema()
        )

    def add_control_reviews_add(self):
        self.add_control_post(
            "commercemeta:add-review",
            title ="add new review",
            href=api.url_for(ReviewCollection),
            schema=Review.json_schema()
        )

    def add_control_edit_user(self, user):
        self.add_control_put(
           "edit",
           api.url_for(UserItem, user=user),
           User.json_schema() 
        )

    def add_control_edit_product(self, username, product):
        self.add_control_put(
           "edit",
           api.url_for(ProductItem, username=username, product=product),
           Product.json_schema() 
        )

    def add_control_edit_category(self, category):
        self.add_control_put(
           "edit",
           api.url_for(CategoryItem, category=category),
           Category.json_schema() 
        )

    def add_control_edit_review(self, username, product):
        self.add_control_put(
           "edit",
           api.url_for(ReviewItem, username=username, product=product),
           Review.json_schema() 
        )

    def add_control_delete_user(self, user):
        self.add_control_delete(
            "commercemeta:delete",
            api.url_for(UserItem, user=user),           
        )

    def add_control_delete_product(self, username, product):
        self.add_control_delete(
            "commercemeta:delete",
            api.url_for(ProductItem, username=username, product=product),    
        )
    
    def add_control_delete_category(self, category):
        self.add_control_delete(
            "commercemeta:delete",
            api.url_for(CategoryItem, category=category),    
        )

    def add_control_delete_review(self, username, product):
        self.add_control_delete(
            "commercemeta:delete",
            api.url_for(ReviewItem, username=username, product=product),    
        )

class UserItem(Resource):
    """
    This class includes the information of an individual user. 
    The class is accessed through api/users/<user>/.
    Please refer to db.py for variables of the class and their nullability.
    """

    def get(self, user):
        """
        This view function fetches the information of the user. Individual
        users are looked up through a particular product and a username. 
        """
        #user = User.query.filter_by(name=user).first()
        #if not user:
            #raise Conflict(description="User_name doesn't exist in db.")
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        
        cached_user = cache.get("user_"+str(user.id))
        if cached_user:
            return cached_user
        
        cache.set("user_"+str(user.id), user.serialize())

        data = CommerceMetaBuilder(user.serialize())
        #print(data)
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("profile", href=USER_PROFILE_URL)
        data.add_control("self", href=request.path)
        data.add_control("collection", href=api.url_for(UserCollection))
        data.add_control_edit_user(user)
        data.add_control_delete_user(user)
        data.add_control(
            "commercemeta:reviews-by",
            href=url_for("reviews_by", user=user)
        )
        data.add_control(
            "commercemeta:products-by",
            href=url_for("products_by_user", user=user)
        )

        return Response(json.dumps(data), 200, mimetype=MASON)

    def put(self, user):
        """
        This function is used to modify the information of an existing user.
        This function requires a valid JSON object with all class variables
        and the structure is validated prior to modifying.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        try:
            validate(request.json, User.json_schema())
            if 'email' in request.json:
                is_valid_email = validate_email(
                    email_address=request.json["email"],
                    check_format=True,
                    check_blacklist=False,
                    check_dns=False,
                    dns_timeout=10,
                    check_smtp=False,
                    smtp_timeout=10)
                if not is_valid_email:
                    raise BadRequest(description="Invalid Email")
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v)) from e_v
        user.deserialize(request.json)
        try:
            db.session.add(user)
            db.session.commit()
            cache.set("user_"+str(user.id), user.serialize())
            cache.delete("users_all")
        except IntegrityError as exc:
            raise Conflict(
                description="Cannot modify username, since it has references in other tables."
            )
        return Response(status=204)

    def delete(self, user):
        """
        This function deletes the user from the db.
        """
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        db.session.delete(user)
        db.session.commit()
        cache.delete("users_all")
        return Response(status=204)


class UserCollection(Resource):
    """
    This class holds the requests for all user information. 
    The class can be accessed through api/users/.
    Through this class one can look up all users of the db and
    create new users.
    """

    def get(self):
        """
        This function fetches the information of all users in the db.
        """
        # get the auth token
        auth_header = request.headers.get('Authorization')
        #print(auth_header)
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        
        cached_users = cache.get("users_all")
        if cached_users:
            return Response(headers={"Content-Type": "application/json"},
                            response=json.dumps(cached_users), status=200)
        
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_users_add()
        data.add_control_products_all()
        data.add_control_reviews_all()

        users = User.query.all()
        #data["items"] = []
        #users_json = []
        for user in users:
            item = CommerceMetaBuilder({
                'name': user.name,
                'password': user.password,
                'email': user.email,
                'role': user.role,
                'avatar': user.avatar,
                # 'products': [product.serialize() for product in user.products],
                # 'reviews': [review.serialize() for review in user.reviews]
            })
            item.add_control("item", api.url_for(UserItem, user=user))
            data["items"].append(item)

        cache.set("users_all", data["items"])
        return Response(headers={"Content-Type": "application/json"},
                        response=json.dumps(data), status=200, mimetype=MASON)

    def post(self):
        """
        This function is used to create new users for the db.
        Please refer to db.py for the necessary variables. Prior to adding
        the user, the JSON structure of the form is validated.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        try:
            validate(request.json, User.json_schema())
            is_valid_email = validate_email(
                email_address=request.json["email"],
                check_format=True,
                check_blacklist=False,
                check_dns=False,
                dns_timeout=10,
                check_smtp=False,
                smtp_timeout=10)
            if not is_valid_email:
                raise BadRequest(description="Invalid Email")

        except ValidationError as e_v:
            raise BadRequest(description=str(e_v)) from e_v

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
            # generate the auth token
            auth_token = user.encode_auth_token(user.name)
            cache.set("user_"+str(user.id), user.serialize())
        except IntegrityError as exc:
            raise Conflict(
                description=f"User with name {request.json['name']} or email \
                {request.json['email']} already exists"
            )
        cache.delete("users_all")
        responseObject = {
            'status': 'success',
            'message': 'Successfully registered.',
            'auth_token': auth_token
        }
        response = make_response(jsonify(responseObject))
        api_url = api.url_for(UserItem, user=user)
        response.headers['location'] = api_url
        response.status_code = 201
        return response

class UserAuth(Resource):
    
    def post(self):
         # get the post data
        post_data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(
                email=post_data.get('email')
              ).first()
            auth_token = user.encode_auth_token(user.name)
            
            if auth_token:
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': auth_token
                }
                response = make_response(jsonify(responseObject))
                response.status_code = 200
                return response
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            response = make_response(jsonify(responseObject))
            response.status_code = 403
            return response
        
    def delete(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not 'token blacklisted' in resp.lower() and not 'signature expired' in resp.lower() and not 'invalid token' in resp.lower():
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    response = make_response(jsonify(responseObject))
                    response.status_code = 200
                    return response
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    response = make_response(jsonify(responseObject))
                    response.status_code = 200
                    return response
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                response = make_response(jsonify(responseObject))
                response.status_code = 401
                return response
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            response = make_response(jsonify(responseObject))
            response.status_code = 403
            return response

class ProductItem(Resource):
    """
    This class includes the requests regarding individual products.
    The class can be accessed from api/users/<username>/products/<product>/.
    The class can be used to getting the information of an individual
    product, modify this information and delete a product from the db.
    """

    def get(self, username, product):
        """
        This function fetches and returns the information of an individual 
        product. 
        """
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        user = User.query.filter_by(name=username).first()
        prod = Product.query.filter_by(name=product).first()
        if not prod:
            raise Conflict(
                description="This product doesn't exist in db."
            )

        cached_product = cache.get("product_"+str(prod.id))
        if cached_product:
            return cached_product

        cache.set("product_"+str(prod.id), prod.serialize())

        data = CommerceMetaBuilder(prod.serialize())
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("profile", href=PRODUCT_PROFILE_URL)
        data.add_control("self", href=request.path)
        data.add_control("collection", href=api.url_for(ProductCollection))
        data.add_control_edit_product(username, product)
        data.add_control_delete_product(username, product)
        data.add_control(
            "commercemeta:products-by", 
            href=url_for("products_by_user", user=username)
        )
        data.add_control(
            "commercemeta:products-by", 
            href=url_for("products_by_category", category=prod.categories[0].name)
        )

        return Response(json.dumps(data), 200, mimetype=MASON)

    def put(self, username, product):
        """
        This function is used to modify an existing product in the db.
        The function requires a valid JSON object, which is validated prior 
        to modifying.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        try:
            validate(request.json, Product.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v)) from e_v
        user = User.query.filter_by(name=username).first()
        prod = Product.query.filter_by(name=product).first()
        if not prod:
            raise Conflict(
                description="This product doesn't exist in db."
            )

        prod.deserialize(request.json)
        #user = None
        #if 'user_name' in request.json:
            #try:
                #user = User.query.filter_by(
                    #name=request.json['user_name']).first()
                #if user:
                    #product.user = user
            #except (IntegrityError, KeyError) as e_i:
                #raise BadRequest

        categories = None
        if 'categories' in request.json:
            try:
                categories = Category.query.filter(
                    Category.name.in_(request.json['categories'])).all()
                if categories:
                    prod.categories = categories
                else:
                    raise BadRequest
            except (IntegrityError, KeyError) as e_i:
                raise BadRequest
        try:
            db.session.add(prod)
            db.session.commit()
            cache.set("prod_"+str(prod.id), prod.serialize())
            cache.delete("products_all")
        except IntegrityError as exc:
            raise Conflict(
                description="Cannot update fields that are referenced in other tables."
            )
        return Response(status=204)

    def delete(self, username, product):
        """
        This function is used to delete a product from the db.
        """
        prod = Product.query.filter_by(name=product).first()
        if prod:
            db.session.delete(prod)
            db.session.commit()
            cache.delete("products_all")
            return Response(status=204)
        return Response(status=404)


class ProductCollection(Resource):
    """
    This class holds the requests for all the products in the db.
    The class can be accessed throuhg api/users/products/.
    Through ProductCollection all product information can be found and
    new products can be created.
    """

    def get(self):
        """
        This function is used to fetch and return the information of all
        products in the db.
        """
        cached_products = cache.get("products_all")
        if cached_products:
            return Response(headers={"Content-Type": "application/json"},
                            response=json.dumps(cached_products), status=200)
        
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_products_add()
        data.add_control_users_all()
        data.add_control_categories_all() 
        products = Product.query.all()
        #products_json = []
        #data["items"] = []
        for product in products:
            item = CommerceMetaBuilder({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'images': json.loads(product.images) if product.images else None,
                'user_name': product.user_name,
                'reviews': [review.serialize(include_product=False, include_user=False) for review in product.reviews],
                'categories': [category.serialize(long=False) for category in product.categories],
            })
            #print(item["user_name"])
            item.add_control("item", api.url_for(ProductItem, product=item["name"], username=item["user_name"]))
            item.add_control(
            "commercemeta:products-by", 
            href=url_for("products_by_user", user=item["user_name"])
            )
            item.add_control(
            "commercemeta:products-by", 
            href=url_for("products_by_category", category=item["categories"][0]["name"])
            )
       
            data["items"].append(item)
        
    
       
        cache.set("products_all", data["items"])
        return Response(headers={"Content-Type": "application/json"},
                        response=json.dumps(data), status=200, mimetype=MASON)

    def post(self):
        """
        This function is used to create new products to the db. New product information
        is expressed as a JSON object, which is validated prior to adding the product.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        try:
            validate(request.json, Product.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        # TODO:: Should a product always have an user? If so, return BadResponse if user is None
        user = User.query.filter_by(
            name=request.json['user_name']).first()

        categories = None
        if 'categories' in request.json:
            categories = Category.query.filter(
                Category.name.in_(request.json['categories'])).all()
            # TODO:: If the categories are not found, should we create them here for the product?

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
       #         description=f'Failed to link product: {request.json["name"]} to \
       # category: {request.json["category"]}'
       #     )
        response = make_response()
        api_url = api.url_for(
            ProductItem, username=user.name, product=product.name)
        response.headers['location'] = api_url
        response.status_code = 201
        return response

class ProductsByUser(Resource):

    def get(self, user):

        product_user = User.query.filter_by(name=user).first()
        products = product_user.products

        #cached_products = cache.get("products_all")
        #if cached_products:
            #return Response(headers={"Content-Type": "application/json"},
                            #response=json.dumps(cached_products), status=200)
        
        #user = User.query.all()
        
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_products_all()

        #products_json = []
        #data["items"] = []
        for product in products:
            item = CommerceMetaBuilder({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'images': json.loads(product.images) if product.images else None,
                'user_name': product.user_name,
                'reviews': [review.serialize(include_product=False, include_user=False) for review in product.reviews],
                'categories': [category.serialize(long=False) for category in product.categories],
            })
            item.add_control("item", api.url_for(ProductItem, product=item["name"]))
            item.add_control("customer", api.url_for(UserItem, user=item["user_name"]))
            data["items"].append(item)
        

        cache.set("products_all", data["items"])
        return Response(headers={"Content-Type": "application/json"},
                        response=json.dumps(data), status=200, mimetype=MASON)


class ProductsByCategory(Resource):

    def get(self, category):

        product_category = Category.query.filter_by(name=category).first()
        products = product_category.products

        #cached_products = cache.get("products_all")
        #if cached_products:
            #return Response(headers={"Content-Type": "application/json"},
                            #response=json.dumps(cached_products), status=200)
        #user = User.query.all()  
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_products_all()
        
        #products_json = []
        #data["items"] = []
        for product in products:
            item = CommerceMetaBuilder({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'images': json.loads(product.images) if product.images else None,
                'user_name': product.user_name,
                'reviews': [review.serialize(include_product=False, include_user=False) for review in product.reviews],
                'categories': [category.serialize(long=False) for category in product.categories],
            })
            item.add_control("item", api.url_for(ProductItem, username=item["user_name"], product=item["name"]))
            item.add_control("category", api.url_for(CategoryItem, category=Category.query.filter_by(name=item["categories"][0]["name"]).first()))
            data["items"].append(item)


        cache.set("products_all", data["items"])
        return Response(headers={"Content-Type": "application/json"},
                        response=json.dumps(data), status=200, mimetype=MASON)


class ReviewItem(Resource):
    """
    This class holds the requests for individual reviews in the db.
    The class can be accessed through api/users/<username>/reviews/<username>/.
    """

    def get(self, username, product):
        """
        This function is used to fetch the information of a single review.
        The function requires a product name and a username.
        """
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        review = Review.query.filter_by(user_name=username).first()
        if not review:
            raise Conflict(
                description="No review to this product by this user.")
        prod = Product.query.filter_by(name=product).first()
        cached_review = cache.get("review_"+str(review.id))
        if cached_review:
            return cached_review

        # TODO:: Are these exceptions dead code?
        # If product doesn't exist, you cannot create a review for it
        # You cannot delete a product without deleting the review first (implement cascading delete)
        # If the review doesn't exist, Conflict is already returned above
        if not prod:
            raise Conflict(
                description="This product doesn't exist in db."
            )
        if not Review.query.filter_by(user_name=username).filter_by(product_name=product).\
                first():
            raise Conflict(
                description="This review doesn't exist in db."
            )
        cache.set("review_"+str(review.id), review.serialize())

        data = CommerceMetaBuilder(review.serialize())
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("profile", href=REVIEW_PROFILE_URL)
        data.add_control("self", href=request.path)
        data.add_control("collection", href=url_for("reviews"))
        data.add_control_edit_review(username, product)
        data.add_control_delete_review(username, product)
        data.add_control(
            "commercemeta:reviews-by",
            href=url_for("reviews_by", user=review.user_name)
        )
        #print(user, username)
        return Response(json.dumps(data), 200, mimetype=MASON)

    def put(self, username, product):
        """
        This function is used to modify the information of an individual review.
        Modifying information should be in JSON form, which is validated prior to modifying.
        Please refer to db.py for further information regarding the parameters.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        try:
            validate(request.json, Review.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v))

        prod = Product.query.filter_by(name=product).first()
        review = Review.query.filter_by(user_name=username).first()
        #print (prod, review)
        if not prod:
            raise Conflict(
                description="This product doesn't exist in db."
            )
        if not Review.query.filter_by(user_name=username).filter_by(product_name=product).first():
            raise Conflict(
                description="This review doesn't exist in db."
            )
        review.deserialize(request.json)
        try:
            db.session.add(review)
            db.session.commit()
            cache.set("review_"+str(review.id), review.serialize())
            cache.delete("reviews_all")

            # TODO:: Is below dead code?
            # The API resource path doesn't
            # exist if the user doesn't exist
            # If the product doesn't exist, you cannot post a review for it
            # You cannot delete a product without deleting the review first (cascading delete)
        except IntegrityError:
            raise Conflict(
                description="Product_name or user_name doesn't exist in db."
            )
        return Response(status=204)

    def delete(self, username, product):
        """
        This function is used to delete reviews from the db.
        """    
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        review = Review.query.filter_by(
            user_name=username, product_name=product).first()
        if review:
            db.session.delete(review)
            db.session.commit()
            cache.delete("reviews_all")
            return Response(status=204)
        return Response(status=409)


class ReviewCollection(Resource):
    """
    This class includes the requests for all of the reviews in the db.
    The class can be accessed through api/users/reviews/.
    Through this class, one can get all reviews of the db and create new ones.
    """

    def get(self):
        """
        This function is used to look up all reviews in the db.
        """
    
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        cached_reviews = cache.get("reviews_all")
        if cached_reviews:
            return Response(headers={"Content-Type": "application/json"},
                            response=json.dumps(cached_reviews), status=200)
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_reviews_add()
        data.add_control_users_all()

        reviews = Review.query.all()
        #reviews_json = []
        #data["items"] = []
        for review in reviews:
            item = CommerceMetaBuilder({
                'id': review.id,
                'description': review.description,
                'rating': review.rating,
                'user_name': review.user_name,
                'product_name': review.product_name,
                # 'user': review.user.serialize(),
                # 'product': review.product.serialize(),
            })
            item.add_control("item", api.url_for(ReviewItem, product=item["product_name"], username=item["user_name"]))
            item.add_control(
            "commercemeta:reviews-by", 
            href=url_for("reviews_by", user=item["user_name"])
            )
            data["items"].append(item)

        cache.set("reviews_all", data["items"])
        return Response(
            headers={"Content-Type": "application/json"},
            response=json.dumps(data),
            status=200, mimetype=MASON
        )  

    def post(self):
        """
        This function is used to post new reviews in the db.
        New review data should be in JSON form, which is validated prior to 
        creating a product. Please refer to db.py for additional parameter information.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
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
                description=request.json['description'] if 'description' in
                request.json else None,
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
        api_url = api.url_for(
            ReviewItem, username=user.name, product=product.name)
        response.headers['location'] = api_url
        response.status_code = 201
        return response

class ReviewsByUser(Resource):
    def get(self, user):
      

        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        
        #review_user = User.query.filter_by(name=user).first()
        reviews = User.query.filter_by(name=user).first().reviews

        #cached_reviews = cache.get("reviews_all")
        #if cached_reviews:
            #return Response(headers={"Content-Type": "application/json"},
                            #response=json.dumps(cached_reviews), status=200)
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_reviews_all()
        #reviews = Review.query.all()
        #reviews_json = []
        #data["items"] = []
        for review in reviews:
            item = CommerceMetaBuilder({
                'id': review.id,
                'description': review.description,
                'rating': review.rating,
                'user_name': review.user_name,
                'product_name': review.product_name,
                # 'user': review.user.serialize(),
                # 'product': review.product.serialize(),
            })
            item.add_control("item", api.url_for(ReviewItem, username=item["user_name"], product=item["product_name"]))
            item.add_control("customer", api.url_for(UserItem, user=user))
            data["items"].append(item)

        cache.set("reviews_all", data["items"])
        return Response(
            headers={"Content-Type": "application/json"},
            response=json.dumps(data),
            status=200, mimetype=MASON
        )  
        

class CategoryItem(Resource):
    """
    This class holds the requests of individual categories. The class
    can be accessed through api/categories/<category:category>/.
    Through this class one can get the information of a category, modify it and
    delete it.
    """

    def get(self, category):
        """
        This function is used to fetch the information of a single category.
        """
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        cached_category = cache.get("category_"+str(category.id))
        if cached_category:
            return cached_category
        cache.set("category_"+str(category.id), category.serialize())

        data = CommerceMetaBuilder(category.serialize())
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("profile", href=CATEGORY_PROFILE_URL)
        data.add_control("self", href=request.path)
        data.add_control("collection", href=api.url_for(CategoryCollection))
        data.add_control_edit_category(category)
        data.add_control_delete_category (category)
        #data.add_control(
            #"commercemeta:products-by", 
            #href=url_for("products_by_category", category=category)
        #)
        return Response(json.dumps(data), 200, mimetype=MASON)
    
    def put(self, category):
        """
        This function is used to modify an existing category. Data for 
        modification should be provided in the form of a JSON object.
        Please refer to db.py for further parameter information.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        try:
            validate(request.json, Category.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v)) from e_v
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
        """
        This function can be used to delete a category.
        """
        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        db.session.delete(category)
        db.session.commit()
        cache.delete("categories_all")
        return Response(status=204)
class CategoryCollection(Resource):
    """
    This class includes the requests for all categories. This class can be 
    accessed through api/categories. Through this class one can 
    get the information of all categories in the db and create new
    categories.
    """

    def get(self):
        """
        This function is used to fetch the information of all categories.
        """
        cached_categories = cache.get("categories_all")
        if cached_categories:
            return Response(headers={"Content-Type": "application/json"},
                            response=json.dumps(cached_categories), status=200)
        data = CommerceMetaBuilder(items=[])
        data.add_namespace("commercemeta", LINK_RELATIONS_URL)
        data.add_control("self", href=request.path)
        data.add_control_categories_add()
        data.add_control_products_all()
        categories = Category.query.all()
        #category_json = []
        data["items"] = []
        for category in categories:
            item = CommerceMetaBuilder({
                'id': category.id,
                'name': category.name,
                'image': category.image,
                # 'products': [product.serialize(long=False) for product in category.products]
            })
            item.add_control("item", api.url_for(CategoryItem, category=category))
            data["items"].append(item)

        cache.set("categories_all", data["items"])
        return Response(headers={"Content-Type": "application/json"},
                        response=json.dumps(data), status=200, mimetype=MASON)
    def post(self):
        """
        This function is used to create new categories. The data for the new
        category should be provided as a JSON object. Please refer to db.py for 
        further parameter information.
        """
        if request.content_type != 'application/json':
            raise UnsupportedMediaType        
        auth_header = request.headers.get('Authorization')
        is_authorized = authorizeUser(auth_header)
        if is_authorized != "authorized":
            return is_authorized
        try:
            validate(request.json, Category.json_schema())
        except ValidationError as e_v:
            raise BadRequest(description=str(e_v)) from e_v
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
        except IntegrityError:
            return Response("Category already exists", 409)
        cache.delete("categories_all")
        response = make_response()
        api_url = api.url_for(CategoryItem, category=category)
        response.headers['location'] = api_url
        response.status_code = 201
        return response
# Routing resources

api.add_resource(UserAuth, "/api/users/auth/")
api.add_resource(UserItem, "/api/users/<user:user>/", endpoint="user")
api.add_resource(UserCollection, "/api/users/", endpoint="users")
api.add_resource(ProductItem, "/api/users/<username>/products/<product>/", endpoint="product")
api.add_resource(ProductCollection,
                 "/api/users/products/",
                 "/api/categories/products/"
                 , endpoint="products")
api.add_resource(ProductsByUser, "/api/users/<user>/products/", endpoint="products_by_user")
api.add_resource(ProductsByCategory, "/api/categories/<category>/products/", endpoint="products_by_category")
api.add_resource(ReviewItem, "/api/users/<username>/reviews/<product>/", endpoint="review")
api.add_resource(ReviewCollection, "/api/users/reviews/", endpoint="reviews")
api.add_resource(ReviewsByUser, "/api/users/<user>/reviews/", endpoint="reviews_by")
api.add_resource(CategoryItem, "/api/categories/<category:category>/", endpoint="category")
api.add_resource(CategoryCollection, "/api/categories/", endpoint="categories")
