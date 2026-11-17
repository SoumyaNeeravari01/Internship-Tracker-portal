from getpass import getpass
from app import app
from models import User
from werkzeug.security import check_password_hash

with app.app_context():
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")

    user = User.query.filter_by(email=email).first()

    if user is None:
        print("ERROR: Admin email not found in this database.")
    elif user.role != "admin":
        print("ERROR: This account is not an admin.")
    elif check_password_hash(user.password_hash, password):
        print("SUCCESS: Admin email and password are correct!")
    else:
        print("ERROR: Password does not match.")