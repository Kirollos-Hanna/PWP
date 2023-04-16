import sys
import random
import requests
from faker import Faker
from path import Path

# directory reach
directory = Path(__file__).abspath()

# setting path
sys.path.append(directory.parent.parent)
from productsapi.db import User, Category, Product, Review, RoleType
from productsapi import create_app, db

faker = Faker()

API_URL = "http://127.0.0.1:5000/"
PASSWORD = "123456"

def generateExponentialRandomValueFrom1To10():
    import numpy as np

    # Set lambda parameter for exponential distribution
    lambdaParam = 1

    # Generate a random value with an exponential distribution
    randomValue = np.random.exponential(scale=1/lambdaParam)

    # Scale and round the result to fit within 1 to 10
    randomValueScaled = 1 + int(round(randomValue)) % 10

    return randomValueScaled


def createUser(data):
    requests.post(f"{API_URL}api/users/", json=data)
    
def createCategory(data, authHeader):
    requests.post(f"{API_URL}api/categories/", json=data, headers=authHeader)
    
def createProduct(data, authHeader):
    requests.post(f"{API_URL}api/users/products/", json=data, headers=authHeader)
    
def createReview(data, authHeader):
    requests.post(f"{API_URL}api/users/reviews/", json=data, headers=authHeader)
    
def authenticateUser(email):
    response = requests.post(f"{API_URL}api/users/auth/", json={"email": email, "password": PASSWORD})
    jsonResponse = response.json()
    return "Bearer " + jsonResponse["auth_token"]
    
def generateSellerData():
    return {
        "name": faker.unique.name(),
        "password": PASSWORD,
        "email": faker.unique.email(),
        "role": RoleType.Seller
    }

def generateCustomerData():
    return {
        "name": faker.unique.name(),
        "password": PASSWORD,
        "email": faker.unique.email(),
        "role": RoleType.Customer
    }
    

def generateCategoryData(category):
    return {
        "name": category
    }
    
def generateProductData(categories, sellerUserName):
    return {
        "name": " ".join(faker.words()) + " " + str(faker.unique.random_number() % 10000),
        "price": faker.random_number() % 10000,
        "user_name": sellerUserName,
        "categories": categories,
        "description": faker.paragraph()
    }

def generateNegativeReviewData(productName, userName, rating):
    negative_adjectives = [
        "terrible",
        "awful",
        "horrible",
        "disappointing",
        "poor",
        "mediocre",
        "dreadful",
        "lousy",
        "pathetic",
        "subpar",
    ]

    negative_verbs = [
        "hate",
        "dislike",
        "regret",
        "lament",
        "resent",
        "deplore",
        "despise",
        "detest",
        "abhor",
        "loathe",
    ]
    adjective = random.choice(negative_adjectives)
    verb = random.choice(negative_verbs)
    reviewDescription = f"I {verb} it! It's {adjective}."
    return {
        "description": reviewDescription,
        "user_name": userName,
        "product_name": productName,
        "rating": rating
    }

    
def generatePositiveReviewData(productName, userName, rating):
    positive_adjectives = [
        "amazing",
        "awesome",
        "fantastic",
        "impressive",
        "outstanding",
        "remarkable",
        "excellent",
        "superb",
        "terrific",
        "incredible",
    ]

    positive_verbs = [
        "love",
        "like",
        "enjoy",
        "recommend",
        "appreciate",
        "admire",
        "value",
        "praise",
        "approve",
        "commend",
    ]
    
    adjective = random.choice(positive_adjectives)
    verb = random.choice(positive_verbs)
    reviewDescription = f"I {verb} it! It's {adjective}."
    return {
        "description": reviewDescription,
        "user_name": userName,
        "product_name": productName,
        "rating": rating
    }
    
config = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False
}

app = create_app()

with app.app_context():
    # Create admin user
    adminUserName = faker.unique.name()
    adminUserEmail = faker.unique.email()
    adminUserData = {
        "name": adminUserName,
        "password": PASSWORD,
        "email": adminUserEmail,
        "role": RoleType.Admin,
        "avatar": None
    }
    print(f"Admin user name and email are: {adminUserName}, {adminUserEmail}")
    createUser(adminUserData)

    # Get auth token
    authToken = authenticateUser(adminUserEmail)

    # Create auth header
    authHeader = {"Authorization": authToken}

    # Create 10 categories
    categoryItems = [
        "Shoes",
        "Shirts",
        "TVs",
        "Phones",
        "Laptops",
        "Tablets",
        "Watches",
        "Headphones",
        "Cameras",
        "Gaming Consoles",
    ]

    for cat in categoryItems:
        createCategory(generateCategoryData(cat), authHeader)
        
    # Create 10 sellers
    for i in range(0,10):
        createUser(generateSellerData())

    # Create 40 customers
    for i in range(0,40):
        createUser(generateCustomerData())

    # Create 10 products for each seller
    sellers = User.query.filter_by(role=RoleType.Seller).all()
    for seller in sellers:
        for i in range(0, 10):
            numCategories = generateExponentialRandomValueFrom1To10()
            categoryIndecies = random.sample(range(0, 10), numCategories)
            productCategories = [categoryItems[i] for i in categoryIndecies]
            productSeller = seller.name
            createProduct(generateProductData(productCategories, productSeller), authHeader)
            

    # Create a review by each customer for each product, alternate between positive and negative reviews randomly
    customers = User.query.filter_by(role=RoleType.Customer).all()
    products = Product.query.all()
    
    for customer in customers:
        for product in products:
            productName = product.name
            customerName = customer.name
            rating = 1 + (faker.random_number() % 10)
            if rating <= 5:
                createReview(generateNegativeReviewData(productName, customerName, rating), authHeader)
            else:
                createReview(generatePositiveReviewData(productName, customerName, rating), authHeader)
       
            
