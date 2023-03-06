import requests

# This file contains UTs for the API
# It is recommended to use pytest, but currently we only have manual tests
# to simulate requests (similar to Postman)

# To add pytest, simply import pytest and write assertions to 
# test functions (e.g., assert type(x.text) == type(""))

def test_get_by_loc(loc):
    api_url = 'http://localhost:5000' + loc
    x = requests.get(api_url)
    print(x.text)
    return x.text

def test_post_to_collection(api_url, data):
    x = requests.post(api_url, json=data)
    #print(x.headers['location'])
    return x.headers['location']

def test_get_collection(api_url):
    x = requests.get(api_url)
    print(x.text)
    return x.text
    
def test_put_to_item(data):
    api_url = 'http://localhost:5000' + loc
    x = requests.put(api_url, json=data)
    print(x.status_code)
    return x.status_code
    


users_api_url = 'http://localhost:5000/api/users/Jaakko'
user_data = {
    "username": "Jaakko",
    "password": "Jaakkonen",
    "email": "jaakko@gmail.com",
    #"avatar": "https://google.com/",
    "role": "Admin"
}

prod_api_url = 'http://localhost:5000/api/products/'
prod_data = {
    "name": "Makkara",
    "price": 19.89,
    "description": "Perus juusto-chili",
    #"images": "https://www.google.com/",
    "user_id": 2
  
}

prod_api_url_put = 'http://localhost:5000/api/products/Makkara/'
put_prod_data = {
    "name": "Makkara",
    "price": 15.15,
    "description": "Perus juusto-chili",
    "user_id": 3
}


review_api_url = 'http://localhost:5000/api/reviews/'
review_data = {
    "description": "ihan hyvaa makkaraa, sopivan tulista.",
    "rating": 5,
    "user_id": 1,
    "product_id": 5
}

categories_api_url = 'http://localhost:5000/api/categories/'
category_data = {
    "name": "NOT_MEAT",
    #"image": "IMAGE_OF_NOT_MEAT_URL",
}

def delete_all():
    api_url = 'http://localhost:5000/api/DROP_TABLE_ALL'
    print(requests.get(api_url).text)

delete_all()

user_loc = test_post_to_collection(users_api_url, user_data) 
test_get_collection(users_api_url)
test_get_by_loc(user_loc)

prod_loc = test_post_to_collection(prod_api_url, prod_data)
test_put_to_item(put_prod_data)
test_get_collection(prod_api_url)
test_get_by_loc(prod_loc)

review_loc = test_post_to_collection(review_api_url, review_data)
test_get_collection(review_api_url)
test_get_by_loc(review_loc)

category_loc = test_post_to_collection(categories_api_url, category_data)
test_get_collection(categories_api_url)
test_get_by_loc(category_loc)
