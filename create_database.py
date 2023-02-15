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
user3 = User(username="kalamies", email="kalamies@email.com", password="hauki", role="Admin")
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

# Add random categories
category1 = Category(name="Instruments")
category2 = Category(name="Electronics")
category3 = Category(name="Books", image="asdasdsad.png")
db.session.add(category1)
db.session.add(category2)
db.session.add(category3)

# Add random products
product1 = Product(name="Fender Stratocaster",
                   description="A brand new Fender Stratocaster Deluxe Edition. Made in USA.",
                   price=1999.99, user_id=user1.id)
product2 = Product(name="Lenovo Thinkpad t420", description="A refurbished business model laptop.", price=149.99,
                   user_id=user1.id)
product3 = Product(name="SAMSUNG 980 SSD 1TB PCle 3.0x4, NVMe M.2 2280",
                   description="UPGRADE TO IMPRESSIVE NVMe SPEED Whether you need a boost for gaming or a seamless workflow for heavy graphics, the 980 is a smart choice for outstanding SSD performance",
                   price=69.99, user_id=user3.id)
db.session.add(product1)
db.session.add(product2)
db.session.add(product3)

# Create relationships between categories and products to allow for categorization of products
product_category1 = Product_categories(product_id=product1.id, category_id=category1.id)
product_category2 = Product_categories(product_id=product2.id, category_id=category2.id)
product_category3 = Product_categories(product_id=product3.id, category_id=category2.id)
db.session.add(product_category1)
db.session.add(product_category2)
db.session.add(product_category3)

# Add random reviews
review1 = Review(rating=4.9, description="An amazing guitar!!", user_id=user2.id, product_id=product1.id)
review2 = Review(rating=0.5, description="Bad laptop, can't run Fortnite with 300 fps.", user_id=user2.id,
                 product_id=product2.id)
review3 = Review(rating=4.4, description="Almost the perfect laptop! Thinkpads rock!", user_id=user3.id,
                 product_id=product2.id)
db.session.add(review1)
db.session.add(review2)
db.session.add(review3)

# Commit the changes
db.session.commit()

# Pop the application context
app_ctx.pop()

print("Database initialized and populated.")
