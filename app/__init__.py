
from flask import Flask
from flask_cors import CORS

from config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Import blueprints
    from app.routes.company_routes import company_bp
    from app.routes.internship_routes import internship_bp
    from app.routes.saved_internship_routes import saved_bp
    from app.routes.hiring_process_routes import hiring_bp

    # Register blueprints
    app.register_blueprint(company_bp)

    app.register_blueprint(
        internship_bp,
        url_prefix="/api/internships"
    )

    app.register_blueprint(
        saved_bp,
        url_prefix="/api/saved-internships"
    )

    app.register_blueprint(
        hiring_bp,
        url_prefix="/api/hiring-process"
    )

    # Home route
    @app.route("/")
    def home():
        return {
            "message": "Welcome to InternTrack API"
        }

    # Health check
    @app.route("/api/health")
    def health():
        return {
            "status": "success",
            "message": "Backend is running"
        }

    # Import models and create database tables
    with app.app_context():
        from app.models.company import Company
        from app.models.internship import Internship
        from app.models.saved_internship import SavedInternship
        from app.models.hiring_process import HiringProcess

        db.create_all()

    return app
