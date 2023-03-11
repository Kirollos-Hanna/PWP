from productsapi.db import User, Category
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound

# Converters are in their own file since they're mapped to app.url_map config
# And it seemed more logical to do the mapping in app.py
# Than cross-import app here

class UserConverter(BaseConverter):

    def to_python(self, user_name):
        db_user = User.query.filter_by(name=user_name).first()
        if db_user is None:
            raise NotFound
        return db_user

    def to_url(self, db_user):
        return db_user.name


class CategoryConverter(BaseConverter):

    def to_python(self, cat_name):
        db_category = Category.query.filter_by(name=cat_name).first()
        if db_category is None:
            raise NotFound
        return db_category
    
    def to_url(self, db_category):
        return db_category.name

