from getpass import getpass
from werkzeug.security import generate_password_hash
from app import app
from database import db
from models import User

with app.app_context():

    email = input("Enter your admin email: ").strip().lower()

    admin = User.query.filter_by(
        email=email,
        role="admin"
    ).first()

    if admin:
        new_password = getpass("Enter your new admin password: ")

        if len(new_password) < 8:
            print("Password must contain at least 8 characters.")
        else:
            admin.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print("Admin password reset successfully!")
    else:
        print("Admin account not found. Check the email.")