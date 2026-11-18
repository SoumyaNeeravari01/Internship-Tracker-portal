from getpass import getpass
from werkzeug.security import generate_password_hash
from app import app
from database import db
from models import User

with app.app_context():

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()
    password = getpass("Enter admin password: ")

    if not name or not email or not password:
        print("All fields are required.")

    elif len(password) < 8:
        print("Password must contain at least 8 characters.")

    elif User.query.filter_by(email=email).first():
        print("This email already exists. No account was changed.")

    else:
        admin = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully!")