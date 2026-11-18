from flask import Flask, jsonify, request, session
from flask_cors import CORS
from functools import wraps
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import db
from models import User


# =====================================
# 1. FLASK APPLICATION CONFIGURATION
# =====================================

app = Flask(__name__)

app.config['SECRET_KEY'] = 'interntrack-development-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interntrack.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)

db.init_app(app)


# =====================================
# 2. ROLE-BASED ACCESS CONTROL
# =====================================

def role_required(required_role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            user_id = session.get('user_id')

            if not user_id:
                return jsonify({
                    "error": "Please login first"
                }), 401

            user = db.session.get(User, user_id)

            if not user:
                session.clear()
                return jsonify({
                    "error": "User not found"
                }), 401

            if user.role != required_role:
                return jsonify({
                    "error": "Access denied"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


# =====================================
# 3. HOME ROUTE
# =====================================

@app.route('/', methods=['GET'])
def home():

    return jsonify({
        "message": "InternTrack Backend is running!"
    }), 200


# =====================================
# 4. STUDENT REGISTRATION
# =====================================

@app.route('/api/auth/register', methods=['POST'])
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON request"
        }), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    college = data.get('college', '').strip()
    branch = data.get('branch', '').strip()
    year = data.get('year', '').strip()

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must contain at least 8 characters"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already registered"
        }), 409

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        role='student',
        college=college,
        branch=branch,
        year=year
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201


# =====================================
# 5. USER LOGIN
# =====================================

@app.route('/api/auth/login', methods=['POST'])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON request"
        }), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if user is None or not check_password_hash(
        user.password_hash, password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    session.clear()
    session['user_id'] = user.id

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


# =====================================
# 6. STUDENT DASHBOARD
# =====================================

@app.route('/api/student/dashboard', methods=['GET'])
@role_required('student')
def student_dashboard():

    return jsonify({
        "message": "Welcome to Student Dashboard"
    }), 200


# =====================================
# 7. ADMIN DASHBOARD
# =====================================

@app.route('/api/admin/dashboard', methods=['GET'])
@role_required('admin')
def admin_dashboard():

    return jsonify({
        "message": "Welcome to Admin Dashboard"
    }), 200


# =====================================
# 8. VIEW USER PROFILE
# =====================================

@app.route('/api/users/me', methods=['GET'])
def get_profile():

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "college": user.college,
        "branch": user.branch,
        "year": user.year
    }), 200


# =====================================
# 9. UPDATE USER PROFILE
# =====================================

@app.route('/api/users/me', methods=['PUT'])
def update_profile():

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON request"
        }), 400

    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({
                "error": "Name cannot be empty"
            }), 400
        user.name = data['name'].strip()

    if 'college' in data:
        user.college = data['college'].strip()

    if 'branch' in data:
        user.branch = data['branch'].strip()

    if 'year' in data:
        user.year = data['year'].strip()

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully"
    }), 200


# =====================================
# 10. USER LOGOUT
# =====================================

@app.route('/api/auth/logout', methods=['POST'])
def logout():

    if not session.get('user_id'):
        return jsonify({
            "error": "You are not logged in"
        }), 401

    session.clear()

    return jsonify({
        "message": "Logout successful"
    }), 200


# =====================================
# 11. CREATE DATABASE TABLES
# =====================================

with app.app_context():
    db.create_all()


# =====================================
# 12. RUN FLASK APPLICATION
# =====================================

if __name__ == '__main__':
    app.run(debug=True)