"""
Converters are in their own file since they're mapped to app.url_map config
And it seemed more logical to do the mapping in app.py
Than cross-import app here
"""
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound
from productsapi.db import User, Category

class UserConverter(BaseConverter):
    """
    This class converts the user from or to url.
    """
    def to_python(self, value):
        db_user = User.query.filter_by(name=value).first()
        if db_user is None:
            raise NotFound
        return db_user
    def to_url(self, db_user):
        return db_user.name

class CategoryConverter(BaseConverter):
    """
    This class converts the category from or to url.
    """
    def to_python(self, value):
        db_category = Category.query.filter_by(name=value).first()
        if db_category is None:
            raise NotFound
        return db_category
    def to_url(self, db_category):
        return db_category[0]["name"]


