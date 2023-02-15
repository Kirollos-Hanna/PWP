from app import app, db, User, Product, Category, Product_categories, Review

# Create an application context
app_ctx = app.app_context()
app_ctx.push()

# WARNING !!
# THIS DELETES PREVIOUSLY MADE TABLES FOR TESTING PURPOSES
db.drop_all()

# Create the tables
db.create_all()

# Add random users
user1 = User(username="pekka", email="pekka@email.com", password="password", role="Seller")
user2 = User(username="matti", email="matti@email.com", password="salasana", role="Customer")
db.session.add(user1)
db.session.add(user2)

# Add random categories
category1 = Category(name="Instruments")
category2 = Category(name="Electronics")
db.session.add(category1)
db.session.add(category2)

# Add random products
product1 = Product(name="Fender Stratocaster",
                   description="A brand new Fender Stratocaster Deluxe Edition. Made in USA.",
                   price=1999.99, user_id=user1.id)
product2 = Product(name="Lenovo Thinkpad t420", description="A refurbished business model laptop.", price=149.99,
                   user_id=user1.id)
db.session.add(product1)
db.session.add(product2)

# Create relationships between categories and products to allow for categorization of products
product_category1 = Product_categories(product_id=product1.id, category_id=category1.id)
product_category2 = Product_categories(product_id=product2.id, category_id=category2.id)
db.session.add(product_category1)
db.session.add(product_category2)

# Add random reviews
review1 = Review(rating=4.9, description="An amazing guitar!!", user_id=user2.id, product_id=product1.id)
review2 = Review(rating=0.5, description="Bad laptop, can't run Fortnite with 300 fps.", user_id=user2.id,
                 product_id=product2.id)
db.session.add(review1)
db.session.add(review2)

# Commit the changes
db.session.commit()

# Pop the application context
app_ctx.pop()

print("Database initialized and populated.")
