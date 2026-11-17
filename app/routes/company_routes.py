from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.company import Company

company_bp = Blueprint("companies", __name__)


@company_bp.route("/api/companies", methods=["POST"])
def create_company():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "Company name is required"}), 400

    if Company.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Company with this name already exists"}), 409

    company = Company(
        name=data.get("name"),
        industry=data.get("industry"),
        description=data.get("description"),
        website=data.get("website"),
        careers_page=data.get("careers_page"),
        location=data.get("location"),
        logo_url=data.get("logo_url"),
    )

    db.session.add(company)
    db.session.commit()

    return jsonify(company.to_dict()), 201


@company_bp.route("/api/companies", methods=["GET"])
def get_companies():
    companies = Company.query.all()
    return jsonify([c.to_dict() for c in companies]), 200


@company_bp.route("/api/companies/<int:company_id>", methods=["GET"])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict()), 200


@company_bp.route("/api/companies/<int:company_id>", methods=["PUT"])
def update_company(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data and data["name"] != company.name:
        if Company.query.filter_by(name=data["name"]).first():
            return jsonify({"error": "Company with this name already exists"}), 409
        company.name = data["name"]

    for field in ("industry", "description", "website", "careers_page", "location", "logo_url"):
        if field in data:
            setattr(company, field, data[field])

    db.session.commit()
    return jsonify(company.to_dict()), 200


@company_bp.route("/api/companies/<int:company_id>", methods=["DELETE"])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return jsonify({"message": "Company deleted successfully"}), 200
