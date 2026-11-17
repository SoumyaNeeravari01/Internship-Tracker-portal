
from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models.company import Company
from app.models.hiring_process import HiringProcess

hiring_bp = Blueprint("hiring_process", __name__)


# 1. Add hiring process information
@hiring_bp.route("/", methods=["POST"])
def add_hiring_process():
    data = request.get_json(silent=True)

    if not data or not data.get("company_id"):
        return jsonify({"error": "Company ID is required"}), 400

    company = db.session.get(Company, data["company_id"])

    if company is None:
        return jsonify({"error": "Company not found"}), 404

    existing = HiringProcess.query.filter_by(
        company_id=data["company_id"]
    ).first()

    if existing:
        return jsonify({
            "error": "Hiring process already exists for this company"
        }), 409

    process = HiringProcess(
        company_id=data["company_id"],
        hiring_stages=data.get("hiring_stages"),
        eligibility=data.get("eligibility"),
        required_skills=data.get("required_skills"),
        required_documents=data.get("required_documents"),
        hiring_season=data.get("hiring_season"),
        official_link=data.get("official_link"),
        source_url=data.get("source_url"),
        verified_on=data.get("verified_on")
    )

    db.session.add(process)
    db.session.commit()

    return jsonify({
        "message": "Hiring process added successfully",
        "hiring_process": process.to_dict()
    }), 201


# 2. View all hiring processes
@hiring_bp.route("/", methods=["GET"])
def get_all_hiring_processes():
    processes = HiringProcess.query.all()

    return jsonify([
        process.to_dict() for process in processes
    ]), 200


# 3. View hiring process by company ID
@hiring_bp.route("/company/<int:company_id>", methods=["GET"])
def get_company_hiring_process(company_id):
    process = HiringProcess.query.filter_by(
        company_id=company_id
    ).first()

    if process is None:
        return jsonify({
            "error": "Hiring process not found"
        }), 404

    return jsonify(process.to_dict()), 200


# 4. Update hiring process
@hiring_bp.route("/<int:process_id>", methods=["PUT"])
def update_hiring_process(process_id):
    process = db.session.get(HiringProcess, process_id)

    if process is None:
        return jsonify({"error": "Hiring process not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    fields = [
        "hiring_stages",
        "eligibility",
        "required_skills",
        "required_documents",
        "hiring_season",
        "official_link",
        "source_url",
        "verified_on"
    ]

    for field in fields:
        if field in data:
            setattr(process, field, data[field])

    db.session.commit()

    return jsonify({
        "message": "Hiring process updated successfully",
        "hiring_process": process.to_dict()
    }), 200


# 5. Delete hiring process
@hiring_bp.route("/<int:process_id>", methods=["DELETE"])
def delete_hiring_process(process_id):
    process = db.session.get(HiringProcess, process_id)

    if process is None:
        return jsonify({"error": "Hiring process not found"}), 404

    db.session.delete(process)
    db.session.commit()

    return jsonify({
        "message": "Hiring process deleted successfully"
    }), 200
