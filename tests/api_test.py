import pytest
import tempfile
import os
from path import Path
import sys

# directory reach
directory = Path(__file__).abspath()

# setting path
sys.path.append(directory.parent.parent)
from productsapi import create_app, db

@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app

    os.close(db_fd)
    # os.unlink(db_fname) # LINE DOES NOT WORK ON WINDOWS


# USER TESTS

# GET ALL USERS
def test_get_all_users_empty_endpoint(app):
    with app.test_client() as c:
        assert_get_request(c, '/api/users/', [], 200)

# POST USER


def test_successful_add_user_minimal(app):
    with app.test_client() as c:
        minimal_user_info = {
            "email": "test42@test.com",
            "username": "kalamies",
            "password": "123456",
            "role": "Customer"
        }
        assert_post_request(
            client=c,
            url='/api/users/',
            expected_location_header="/api/users/kalamies/",
            expected_response_status=201,
            json_body=minimal_user_info
        )

        minimal_user_info["products"] = []
        minimal_user_info["reviews"] = []
        minimal_user_info["avatar"] = None

        assert_get_request(c, '/api/users/', [minimal_user_info], 200)


def test_add_user_full_successful(app):
    with app.test_client() as c:
        full_user_info = {
            "email": "test42@test.com",
            "username": "kalamies",
            "password": "123456",
            "role": "Customer",
            "avatar": "https://www.google.com/"
        }

        assert_post_request(
            client=c,
            url='/api/users/',
            expected_location_header="/api/users/kalamies/",
            expected_response_status=201,
            json_body=full_user_info
        )

        full_user_info["products"] = []
        full_user_info["reviews"] = []
        assert_get_request(c, '/api/users/', [full_user_info], 200)


def test_add_user_full_unsuccessful_avatar(app):
    with app.test_client() as c:
        full_user_info = {
            "email": "test42@test.com",
            "username": "kalamies",
            "password": "123456",
            "role": "Customer",
            "avatar": "test.jpg"
        }

        response = c.post('/api/users/', json=full_user_info)
        assert response.status_code == 400

# TODO
# def test_add_user_full_unsuccessful_email(app):
#     with app.test_client() as c:
#         full_user_info = {
#             "email": "test42",
#             "username": "kalamies",
#             "password": "123456",
#             "role": "Customer",
#             "avatar": "https://www.google.com/"
#         }

#         response = c.post('/api/users/', json=full_user_info)
#         assert response.status_code == 400


def test_add_and_get_single_user_endpoint(app):
    with app.test_client() as c:
        assert_get_request(c, '/api/users/', [], 200)

        full_user_info = {
            "email": "test42@test.com",
            "username": "palomies",
            "password": "654321",
            "role": "Seller",
            "avatar": "https://www.google.com/"
        }

        assert_post_request(
            client=c,
            url='/api/users/',
            expected_location_header="/api/users/palomies/",
            expected_response_status=201,
            json_body=full_user_info
        )

        full_user_info["id"] = 1
        full_user_info["products"] = []
        full_user_info["reviews"] = []
        assert_get_request(c, '/api/users/palomies/', full_user_info, 200)


def test_add_multiple_and_get_all_users_endpoint(app):
    with app.test_client() as c:
        assert_get_request(c, '/api/users/', [], 200)

        full_user_info_1 = {
            "email": "test42@test.com",
            "username": "palomies",
            "password": "654321",
            "role": "Seller",
            "avatar": "https://www.google.com/"
        }

        full_user_info_2 = {
            "email": "test1234@test.com",
            "username": "kalamies",
            "password": "654321",
            "role": "Customer",
            "avatar": "https://www.google.com/"
        }

        assert_post_request(
            client=c,
            url='/api/users/',
            expected_location_header="/api/users/palomies/",
            expected_response_status=201,
            json_body=full_user_info_1
        )

        assert_post_request(
            client=c,
            url='/api/users/',
            expected_location_header="/api/users/kalamies/",
            expected_response_status=201,
            json_body=full_user_info_2
        )

        full_user_info_1["products"] = full_user_info_2["products"] = []
        full_user_info_1["reviews"] = full_user_info_2["reviews"] = []
        assert_get_request(
            c, '/api/users/', [full_user_info_1, full_user_info_2], 200)

# PUT USER


def test_update_user_full_successful(app):
    with app.test_client() as c:
        full_user_info = {
            "email": "test42@test.com",
            "username": "kalamies",
            "password": "123456",
            "role": "Customer",
            "avatar": "https://www.google.com/"
        }

        response = c.post('/api/users/', json=full_user_info)

        updated_full_user_info = {
            "email": "test423@test.com",
            "username": "kalamies2",
            "password": "1234561",
            "role": "Seller",
            "avatar": "https://www.google2.com/"
        }
        response_put = c.put(
            '/api/users/' + full_user_info['username'] + "/", json=updated_full_user_info)

        assert response.status_code == 201
        assert response.headers['location'] == "/api/users/kalamies/"

        assert response_put.status_code == 204

        updated_full_user_info["products"] = []
        updated_full_user_info["reviews"] = []
        assert_get_request(c, '/api/users/', [updated_full_user_info], 200)


def test_update_user_full_unsuccessful_email(app):
    with app.test_client() as c:
        full_user_info = {
            "email": "test42@test.com",
            "username": "kalamies",
            "password": "123456",
            "role": "Customer",
            "avatar": "https://www.google.com/"
        }

        response = c.post('/api/users/', json=full_user_info)

        updated_full_user_info = {
            "email": "test423@test.com",
            "username": "kalamies2",
            "password": "1234561",
            "role": "Seller",
            "avatar": "test.jpg"
        }
        response_put = c.put(
            '/api/users/' + full_user_info['username'] + "/", json=updated_full_user_info)

        assert response.status_code == 201
        assert response.headers['location'] == "/api/users/kalamies/"

        assert response_put.status_code == 400

        full_user_info["products"] = []
        full_user_info["reviews"] = []
        assert_get_request(c, '/api/users/', [full_user_info], 200)

# DELETE USER


def test_delete_user_full(app):
    with app.test_client() as c:
        full_user_info = {
            "email": "test42@test.com",
            "username": "kalamies",
            "password": "123456",
            "role": "Customer",
            "avatar": "https://www.google.com/"
        }

        response = c.post('/api/users/', json=full_user_info)

        response_delete = c.delete(
            '/api/users/' + full_user_info['username'] + "/")

        assert response.status_code == 201
        assert response.headers['location'] == "/api/users/kalamies/"

        assert response_delete.status_code == 204

        assert_get_request(c, '/api/users/', [], 200)


# PRODUCT TESTS
dummy_user_info = {
    "email": "test42@test.com",
    "username": "kalamies",
    "password": "123456",
    "role": "Customer",
    "avatar": "https://www.google.com/"
}

dummy_category_info = {
    "name": "test_category",
    "image": "https://www.google.com/"
}

minimal_product_info = {
    "name": "test_product",
    "price": 5.3,
    "user_id": 1
}

minimal_product_info_response = {
    "name": "test_product",
    "price": 5.3,
    "id": 1,
    "description": None,
    "images": None,
}

full_product_info = {
    "name": "test_product",
    "price": 5.3,
    "user_id": 1,
    "images": ["https://www.google.com/", "https://www.google.com/"],
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
    "categories": ["test_category"]
}

full_product_info_2 = {
    "name": "test_product2",
    "price": 5.3,
    "user_id": 1,
    "images": ["https://www.google.com/", "https://www.google.com/"],
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
    "categories": ["test_category"]
}

updated_full_product_info = {
    "name": "test_product_updated",
    "price": 6.4,
    "images": ["https://www.yahoo.com/"],
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    """,
}

updated_full_product_info_bad_images = {
    "name": "test_product_updated",
    "price": 6.4,
    "images": ["test.jpg"],
}

updated_full_product_info_bad_user = {
    "name": "test_product_updated",
    "price": 6.4,
    "images": ["https://www.yahoo.com/"],
    "user_id": 5,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    """,
}

updated_full_product_info_bad_categories = {
    "name": "test_product_updated",
    "price": 6.4,
    "images": ["https://www.yahoo.com/"],
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    """,
    "categories": ["nonexistent_category"]
}

# GET ALL PRODUCTS


def test_get_all_products_empty_endpoint(app):
    with app.test_client() as c:
        assert_get_request(c, '/api/products/', [], 200)


# POST PRODUCT
def test_successful_add_product_minimal(app):
    with app.test_client() as c:
        add_model(
            c,
            "/api/users/",
            dummy_user_info
        )
        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product/",
            expected_response_status=201,
            json_body=minimal_product_info
        )
        local_info = {**minimal_product_info}
        local_info["id"] = 1
        local_info["images"] = None
        local_info["description"] = None
        local_info["reviews"] = []
        local_info["categories"] = []

        assert_get_request(c, '/api/products/', [local_info], 200)


def test_successful_add_product_full(app):
    with app.test_client() as c:
        add_product_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product/",
            expected_response_status=201,
            json_body=full_product_info
        )

        local_info = {**full_product_info}
        local_info["id"] = 1
        local_info["reviews"] = []
        local_info["categories"] = [{"id": 1, **dummy_category_info}]

        assert_get_request(c, '/api/products/', [local_info], 200)


def test_add_product_full_unsuccessful_avatars(app):
    with app.test_client() as c:
        add_model(
            c,
            "/api/users/",
            dummy_user_info
        )

        full_product_info_bad_images = {**full_product_info}
        full_product_info_bad_images["images"] = [
            "https://www.google.com/", "test.jpg"]
        response = c.post('/api/products/', json=full_product_info_bad_images)
        assert response.status_code == 400


def test_add_product_full_unsuccessful_missing_user(app):
    with app.test_client() as c:
        response = c.post('/api/products/', json=full_product_info)
        assert response.status_code == 409


def test_add_and_get_single_product_endpoint(app):
    with app.test_client() as c:

        add_product_prereqs(c)

        assert_get_request(c, '/api/products/', [], 200)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product/",
            expected_response_status=201,
            json_body=full_product_info
        )

        local_info = {**full_product_info}
        local_info["id"] = 1
        local_info["categories"] = [{"id": 1, **dummy_category_info}]
        local_info["reviews"] = []
        local_info.pop("user_id")

        assert_get_request(c, '/api/products/test_product/', local_info, 200)


def test_add_multiple_and_get_all_products_endpoint(app):
    with app.test_client() as c:

        add_product_prereqs(c)

        assert_get_request(c, '/api/products/', [], 200)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product/",
            expected_response_status=201,
            json_body=full_product_info
        )

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product2/",
            expected_response_status=201,
            json_body=full_product_info_2
        )

        local_info = {**full_product_info}
        local_info_2 = {**full_product_info_2}
        local_info["id"] = 1
        local_info_2["id"] = 2

        local_info["reviews"] = local_info_2["reviews"] = []
        local_info["categories"] = local_info_2["categories"] = [
            {"id": 1, **dummy_category_info}]
        assert_get_request(c, '/api/products/',
                           [local_info, local_info_2], 200)


def test_unsuccessful_add_multiple_products_same_name(app):
    with app.test_client() as c:
        add_model(
            c,
            "/api/users/",
            dummy_user_info
        )
        assert_get_request(c, '/api/products/', [], 200)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product/",
            expected_response_status=201,
            json_body=full_product_info
        )

        assert_failed_post_request(
            client=c,
            url='/api/products/',
            expected_response_status=409,
            json_body=full_product_info
        )


# PUT PRODUCT
def test_update_product_full_successful(app):
    with app.test_client() as c:
        add_product_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/" +
                full_product_info['name'] + "/",
            expected_response_status=201,
            json_body=full_product_info
        )

        response_put = c.put(
            '/api/products/' + full_product_info['name'] + "/", json=updated_full_product_info)

        assert response_put.status_code == 204

        updated_local_info = {**updated_full_product_info}
        updated_local_info["id"] = 1
        updated_local_info["reviews"] = []
        updated_local_info["user_id"] = 1
        updated_local_info["categories"] = [{"id": 1, **dummy_category_info}]
        assert_get_request(c, '/api/products/', [updated_local_info], 200)


def test_update_product_full_unsuccessful_images(app):
    make_faulty_product_put_requests(
        app, updated_full_product_info_bad_images, 400)


def test_update_product_full_unsuccessful_user(app):
    make_faulty_product_put_requests(
        app, updated_full_product_info_bad_user, 400)


def test_update_product_full_unsuccessful_category(app):
    make_faulty_product_put_requests(
        app, updated_full_product_info_bad_categories, 400)

# DELETE PRODUCT


def test_delete_product_full(app):
    with app.test_client() as c:
        add_product_prereqs(c)

        assert_get_request(c, '/api/products/', [], 200)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/test_product/",
            expected_response_status=201,
            json_body=full_product_info
        )

        response_delete = c.delete(
            '/api/products/' + full_product_info['name'] + "/")

        assert response_delete.status_code == 204

        assert_get_request(c, '/api/products/', [], 200)


# REVIEW TESTS
minimal_review_info = {
    "rating": 2.5,
    "user_id": 1,
    "product_id": 1,
}

minimal_review_info_below_lowest_threshold = {
    "rating": 0.9,
    "user_id": 1,
    "product_id": 1,
}

minimal_review_info_lowest_threshold = {
    "rating": 1,
    "user_id": 1,
    "product_id": 1,
}

minimal_review_info_highest_threshold = {
    "rating": 10,
    "user_id": 1,
    "product_id": 1,
}

minimal_review_info_above_highest_threshold = {
    "rating": 10.1,
    "user_id": 1,
    "product_id": 1,
}

full_review_info = {
    "rating": 2.5,
    "user_id": 1,
    "product_id": 1,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
}

full_review_info_2 = {
    "rating": 8.5,
    "user_id": 1,
    "product_id": 1,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
}

full_review_info_bad_rating = {
    "rating": 12.5,
    "user_id": 1,
    "product_id": 1,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
}

full_review_info_bad_user = {
    "rating": 2.5,
    "user_id": 5,
    "product_id": 1,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
}

full_review_info_bad_product = {
    "rating": 2.5,
    "user_id": 1,
    "product_id": 2,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    Sed sem libero, venenatis vitae risus eget, sagittis tempus lacus. Aenean non faucibus dui. Phasellus placerat mi tellus, vitae vehicula urna mattis sit amet. Ut eleifend, libero ut rutrum auctor, tellus felis imperdiet erat, in lacinia libero lacus a est. Nam enim libero, maximus id maximus eu, faucibus non quam. Praesent sodales urna in orci aliquam lobortis. Sed a posuere lorem. Proin sed odio ullamcorper arcu luctus mattis. Curabitur in finibus magna. Curabitur non nisl et dui laoreet hendrerit. Donec tempor iaculis egestas. Phasellus convallis libero feugiat massa egestas posuere. Morbi leo nibh, gravida dapibus nulla sed, vestibulum blandit eros. Nulla ut ante metus. Sed nec cursus est. Ut in ex quis ligula dictum blandit.
    """,
}

updated_full_review_info = {
    "rating": 3.5,
    "description": """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse viverra eu sapien non pulvinar. Pellentesque sit amet diam lectus. Vestibulum blandit lacinia justo sed molestie. Nunc tempor est tortor, sit amet suscipit erat molestie ac. Donec ullamcorper luctus mi vel elementum. Aliquam vel condimentum magna. Etiam sed ipsum tristique, malesuada leo at, tempus tortor. Vivamus dictum orci vel metus auctor laoreet. Pellentesque et eleifend quam. Etiam vehicula arcu orci, euismod accumsan dolor placerat at. Mauris ligula sapien, ornare sit amet lobortis a, interdum vitae quam. Nam sed consectetur nunc. In tincidunt congue magna quis venenatis. Vivamus ullamcorper felis eu viverra pulvinar. Nulla sed ipsum nibh. Nulla vitae nisl non diam gravida semper fermentum nec orci.

    Duis vitae molestie sem. Cras sit amet sapien nec nibh faucibus venenatis. Sed eget nibh posuere, molestie elit vel, faucibus arcu. Sed consequat tellus at lacus placerat, et posuere mi sagittis. Nullam molestie sapien pharetra mollis vulputate. Duis efficitur tristique arcu sed tristique. Curabitur vel mattis massa, ut efficitur turpis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.

    """,
}

updated_full_review_info_fail_user = {
    "user_id": 1
}

updated_full_review_info_fail_product = {
    "product_id": 1
}

# GET ALL REVIEWs


def test_get_all_reviews_empty_endpoint(app):
    with app.test_client() as c:
        assert_get_request(c, '/api/reviews/', [], 200)


# POST REVIEW

def test_successful_add_review_minimal(app):
    with app.test_client() as c:
        add_review_prereqs(c)
        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=minimal_review_info
        )
        local_info = {**minimal_review_info}
        local_info["id"] = 1
        local_info["description"] = None

        assert_get_request(c, '/api/reviews/', [local_info], 200)


def test_successful_add_review_full(app):
    with app.test_client() as c:
        add_review_prereqs(c)
        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=full_review_info
        )
        local_info = {**full_review_info}
        local_info["id"] = 1

        assert_get_request(c, '/api/reviews/', [local_info], 200)


def test_add_review_full_unsuccessful_rating(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        response = c.post('/api/reviews/', json=full_review_info_bad_rating)
        assert response.status_code == 400


def test_add_review_minimal_ratings(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=minimal_review_info_lowest_threshold
        )

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/2/",
            expected_response_status=201,
            json_body=minimal_review_info_highest_threshold
        )

        assert_failed_post_request(
            client=c,
            url='/api/reviews/',
            expected_response_status=400,
            json_body=minimal_review_info_above_highest_threshold
        )

        assert_failed_post_request(
            client=c,
            url='/api/reviews/',
            expected_response_status=400,
            json_body=minimal_review_info_below_lowest_threshold
        )


def test_add_review_full_unsuccessful_user(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        response = c.post('/api/reviews/', json=full_review_info_bad_user)
        assert response.status_code == 409


def test_add_review_full_unsuccessful_product(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        response = c.post('/api/reviews/', json=full_review_info_bad_product)
        assert response.status_code == 409


def test_add_and_get_single_review_endpoint(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        assert_get_request(c, '/api/reviews/', [], 200)

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=full_review_info
        )

        local_info = {**full_review_info}
        local_info["id"] = 1
        local_info["user"] = {"id": 1, **dummy_user_info}
        local_info["product"] = minimal_product_info_response
        local_info.pop("user_id")
        local_info.pop("product_id")

        assert_get_request(c, '/api/reviews/1/', local_info, 200)


def test_add_multiple_and_get_all_reviews_endpoint(app):
    with app.test_client() as c:

        add_review_prereqs(c)

        assert_get_request(c, '/api/reviews/', [], 200)

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=full_review_info
        )

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/2/",
            expected_response_status=201,
            json_body=full_review_info_2
        )

        local_info = {**full_review_info}
        local_info["id"] = 1

        local_info = {**full_review_info}
        local_info_2 = {**full_review_info_2}
        local_info["id"] = 1
        local_info_2["id"] = 2

        assert_get_request(c, '/api/reviews/',
                           [local_info, local_info_2], 200)


# PUT REVIEW
def test_update_review_successful(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=full_review_info
        )

        response_put = c.put(
            '/api/reviews/1/', json=updated_full_review_info)

        assert response_put.status_code == 204

        updated_local_info = {**updated_full_review_info}
        updated_local_info["id"] = 1
        updated_local_info["user_id"] = 1
        updated_local_info["product_id"] = 1
        assert_get_request(c, '/api/reviews/', [updated_local_info], 200)


def test_update_review_unsuccessful(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=full_review_info
        )

        assert_failed_put_request(
            client=c,
            url='/api/reviews/1/',
            expected_response_status=400,
            json_body=updated_full_review_info_fail_product
        )

        assert_failed_put_request(
            client=c,
            url='/api/reviews/1/',
            expected_response_status=400,
            json_body=updated_full_review_info_fail_user
        )


# DELETE REVIEW
def test_delete_review_full(app):
    with app.test_client() as c:
        add_review_prereqs(c)

        assert_get_request(c, '/api/reviews/', [], 200)

        assert_post_request(
            client=c,
            url='/api/reviews/',
            expected_location_header="/api/reviews/1/",
            expected_response_status=201,
            json_body=full_review_info
        )

        response_delete = c.delete(
            '/api/reviews/1/')

        assert response_delete.status_code == 204

        assert_get_request(c, '/api/reviews/', [], 200)


# CATEGORY TESTS

minimal_category_info = {
    "name": "test_category"
}


full_category_info = {
    "name": "test_category",
    "image": "https://www.google.com/",
    "product_names": ["test_product"]
}

full_category_info_2 = {
    "name": "test_category2",
    "image": "https://www.google.com/",
    "product_names": ["test_product"]
}

full_category_info_bad_image = {
    "name": "test_category",
    "image": "test.jpg",
    "product_names": ["test_product"]
}
full_category_info_bad_product = {
    "name": "test_category",
    "image": "https://www.google.com/",
    "product_names": ["nonexistent_product"]
}

updated_full_category_info = {
    "name": "test_category3",
    "image": "https://www.yahoo.com/",
    "product_names": ["test_product"]
}

updated_full_category_info_bad_image = {
    "image": "test.jpg",
}
updated_full_category_info_bad_products = {
    "product_names": ["nonexistent_product"]
}
# GET ALL CATEGORIES


def test_get_all_categories_empty_endpoint(app):
    with app.test_client() as c:
        assert_get_request(c, '/api/categories/', [], 200)


# POST CATEGORY


def test_successful_add_category_minimal(app):
    with app.test_client() as c:
        add_category_prereqs(c)
        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=minimal_category_info
        )
        local_info = {**minimal_category_info}
        local_info["id"] = 1
        local_info["image"] = None

        assert_get_request(c, '/api/categories/', [local_info], 200)


def test_successful_add_category_full(app):
    with app.test_client() as c:
        add_category_prereqs(c)
        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=full_category_info
        )
        local_info = {**full_category_info}
        local_info["id"] = 1
        local_info.pop("product_names")

        assert_get_request(c, '/api/categories/', [local_info], 200)


def test_unsuccessful_add_category_full_bad_image(app):
    with app.test_client() as c:
        add_category_prereqs(c)
        assert_failed_post_request(
            client=c,
            url='/api/categories/',
            expected_response_status=400,
            json_body=full_category_info_bad_image
        )


def test_unsuccessful_add_category_full_bad_product(app):
    with app.test_client() as c:
        add_category_prereqs(c)
        assert_failed_post_request(
            client=c,
            url='/api/categories/',
            expected_response_status=400,
            json_body=full_category_info_bad_product
        )


def test_add_and_get_single_category_endpoint(app):
    with app.test_client() as c:
        add_category_prereqs(c)

        assert_get_request(c, '/api/categories/', [], 200)

        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=full_category_info
        )

        local_info = {**full_category_info}
        local_info["id"] = 1
        local_product_info = {**minimal_product_info,
                              "description": None, "images": None, "id": 1}
        local_product_info.pop("user_id")
        local_info["products"] = [local_product_info]
        local_info.pop("product_names")

        assert_get_request(
            c, '/api/categories/test_category/', local_info, 200)


def test_add_multiple_and_get_all_categories_endpoint(app):
    with app.test_client() as c:

        add_category_prereqs(c)

        assert_get_request(c, '/api/categories/', [], 200)

        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=full_category_info
        )

        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category2/",
            expected_response_status=201,
            json_body=full_category_info_2
        )

        local_info = {**full_category_info}
        local_info_2 = {**full_category_info_2}
        local_info["id"] = 1
        local_info_2["id"] = 2
        local_info.pop("product_names")
        local_info_2.pop("product_names")

        assert_get_request(c, '/api/categories/',
                           [local_info, local_info_2], 200)


# PUT CATEGORY
def test_update_category_successful(app):
    with app.test_client() as c:
        add_category_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=full_category_info
        )

        response_put = c.put(
            '/api/categories/test_category/', json=updated_full_category_info)

        assert response_put.status_code == 204

        updated_local_info = {**updated_full_category_info}
        updated_local_info["id"] = 1
        updated_local_info.pop("product_names")
        assert_get_request(c, '/api/categories/', [updated_local_info], 200)


def test_update_category_unsuccessful(app):
    with app.test_client() as c:
        add_category_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=full_category_info
        )

        assert_failed_put_request(
            client=c,
            url='/api/categories/test_category/',
            expected_response_status=400,
            json_body=updated_full_category_info_bad_image
        )

        assert_failed_put_request(
            client=c,
            url='/api/categories/test_category/',
            expected_response_status=400,
            json_body=updated_full_category_info_bad_products
        )


# DELETE CATEGORY
def test_delete_category_full(app):
    with app.test_client() as c:
        add_category_prereqs(c)

        assert_get_request(c, '/api/categories/', [], 200)

        assert_post_request(
            client=c,
            url='/api/categories/',
            expected_location_header="/api/categories/test_category/",
            expected_response_status=201,
            json_body=full_category_info
        )

        response_delete = c.delete(
            '/api/categories/test_category/')

        assert response_delete.status_code == 204

        assert_get_request(c, '/api/categories/', [], 200)


# Helper Functions
def assert_get_request(client, url, expected_response_body, expected_response_status):
    response = client.get(url)
    json_response = response.get_json()
    assert response.status_code == expected_response_status
    assert json_response == expected_response_body


def assert_post_request(client, url, expected_location_header, expected_response_status, json_body):
    response = client.post(url, json=json_body)
    assert response.status_code == expected_response_status
    assert response.headers['location'] == expected_location_header


def assert_failed_post_request(client, url, expected_response_status, json_body):
    response = client.post(url, json=json_body)
    assert response.status_code == expected_response_status


def assert_failed_put_request(client, url, expected_response_status, json_body):
    response = client.put(url, json=json_body)
    assert response.status_code == expected_response_status


def add_model(client, url, json_body):
    client.post(url, json=json_body)


def add_product_prereqs(c):
    add_model(
        c,
        "/api/users/",
        dummy_user_info
    )

    add_model(
        c,
        "/api/categories/",
        dummy_category_info
    )


def make_faulty_product_put_requests(app, json_data, expected_response_code):
    with app.test_client() as c:
        add_product_prereqs(c)

        assert_post_request(
            client=c,
            url='/api/products/',
            expected_location_header="/api/products/" +
                full_product_info['name'] + "/",
            expected_response_status=201,
            json_body=full_product_info
        )

        response_put = c.put('/api/products/' +
                             full_product_info['name'] + "/", json=json_data)

        assert response_put.status_code == expected_response_code


def add_review_prereqs(c):
    add_product_prereqs(c)

    add_model(
        c,
        "/api/products/",
        minimal_product_info
    )


def add_category_prereqs(c):

    add_model(
        c,
        "/api/users/",
        dummy_user_info
    )

    add_model(
        c,
        "/api/products/",
        minimal_product_info
    )
