# PWP SPRING 2023
# E-Commerce API
E-Commerce API is a Python API for managing and retrieving information about products, reviews, categories, and users in an online store.
# Group information
* Student 1. Samuli Koponen and email
* Student 2. Petri Kiviniemi and email
* Student 3. Mimmi Kähkönen and email
* Student 4. Kirollos Hanna and email

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Installation

Clone the repository to your machine.

```bash
git clone https://github.com/Kirollos-Hanna/PWP.git
```
Change the directory to the project's directory and install the required dependencies.

```bash
cd PWP/
pip install -r requirements.txt
```
## Usage
Run python interpreter inside the project's directory.
```bash
python
```
First we create a SQLite database with SQLalchemy.
```python
from app import db, app
ctx = app.app_context()
ctx.push()
db.create_all()
ctx.pop()
```
Add an product, review, category or user in to the database. In the example below, we will add an user.
```python
from app import app, db, User

with app.app_context():
    user = User(username='Matti', email='matti.meikalainen@gmail.com', password='password', role='seller')
    db.session.add(user)
    db.session.commit()
```
Start the server.
```bash
flask run
```
## License

[GNU General Public License Version 3](https://github.com/Kirollos-Hanna/PWP/blob/main/LICENSE)
