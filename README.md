# PWP SPRING 2023
# E-Commerce API
E-Commerce API is a Python API for managing and retrieving information about products, reviews, categories, and users in an online store.
# Group information
* Student 1. Samuli Koponen and email
* Student 2. Petri Kiviniemi and email
* Student 3. Mimmi Kähkönen and email
* Student 4. Kirollos Hanna and email

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Technologies Used

This project uses the following technologies:

* Flask: a Python web framework used for building web applications
* SQLAlchemy: a Python library used for accessing and managing databases using the Python SQL Toolkit and Object-Relational Mapping (ORM) system

## Installation

Clone the repository to your machine.

```bash
git clone https://github.com/Kirollos-Hanna/PWP.git
```
Change the directory to the project's directory.

```bash
cd PWP/
```
Install the required dependencies.
```bash
pip install -r requirements.txt
```
Run the create_database-script to initialize and populate the database.
```bash
python .\/productsapi/create_database.py
```
## Usage

Start the server.
```bash
FLASK_APP=productsapi flask run
```
Run the tests.
```bash
python ut.py
```

Alternatively, run pytest.
```bash
pytest
```
For verbose logging use the `-vv` flag
```bash
pytest -vv
```
**Usage examples:**
```bash
# Create an user called "johndoe"
curl -X POST -H "Content-Type: application/json" -d '{"username":"johndoe", "password":"password", "email":"johndoe@mail.com", "role":"Seller"}' http://localhost:5000/api/users/
# Retrieve user's "johndoe" information and check his id
curl -X GET http://localhost:5000/api/users/johndoe/
# Add a product to sell for user "johndoe" using his id
curl -X POST -H "Content-Type: application/json" -d '{"name":"1984", "user_id": 4, "price":19.99, "description":"Written by George Orwell", "categories":["Books"]}' http://localhost:5000/api/products/
# Retrieve all products
curl -X GET http://127.0.0.1:5000/api/products/
# Retrieve the added product 1984
curl -X GET http://localhost:5000/api/products/1984/

```
## License

[GNU General Public License Version 3](https://github.com/Kirollos-Hanna/PWP/blob/main/LICENSE)
