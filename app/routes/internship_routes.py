
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, cast, Float

from app.extensions import db
from app.models.internship import Internship
from app.models.company import Company

internship_bp = Blueprint("internships", __name__)


# 1. Add a new internship
@internship_bp.route("/", methods=["POST"])
def add_internship():
    data = request.get_json(silent=True)

    if not data or not data.get("title"):
        return jsonify({"error": "Internship title is required"}), 400

    company_id = data.get("company_id")

    if not company_id:
        return jsonify({"error": "Company ID is required"}), 400

    company = db.session.get(Company, company_id)

    if company is None:
        return jsonify({"error": "Company not found"}), 404

    internship = Internship(
        company_id=company_id,
        title=data.get("title"),
        description=data.get("description"),
        skills_required=data.get("skills_required"),
        location=data.get("location"),
        stipend=data.get("stipend"),
        duration=data.get("duration"),
        work_mode=data.get("work_mode"),
        eligibility=data.get("eligibility"),
        deadline=data.get("deadline"),
        application_url=data.get("application_url")
    )

    db.session.add(internship)
    db.session.commit()

    return jsonify({
        "message": "Internship added successfully",
        "internship": internship.to_dict()
    }), 201


# 2. Get all internships
@internship_bp.route("/", methods=["GET"])
def get_internships():
    internships = Internship.query.all()

    return jsonify([
        internship.to_dict() for internship in internships
    ]), 200


# 3. Get internship by ID
@internship_bp.route("/<int:internship_id>", methods=["GET"])
def get_internship(internship_id):
    internship = db.session.get(Internship, internship_id)

    if internship is None:
        return jsonify({"error": "Internship not found"}), 404

    return jsonify(internship.to_dict()), 200


# 4. Update an internship
@internship_bp.route("/<int:internship_id>", methods=["PUT"])
def update_internship(internship_id):
    internship = db.session.get(Internship, internship_id)

    if internship is None:
        return jsonify({"error": "Internship not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if "company_id" in data:
        company = db.session.get(Company, data["company_id"])

        if company is None:
            return jsonify({"error": "Company not found"}), 404

        internship.company_id = data["company_id"]

    fields = [
        "title", "description", "skills_required",
        "location", "stipend", "duration", "work_mode",
        "eligibility", "deadline", "application_url"
    ]

    for field in fields:
        if field in data:
            if field == "title" and not data[field]:
                return jsonify({"error": "Title cannot be empty"}), 400

            setattr(internship, field, data[field])

    db.session.commit()

    return jsonify({
        "message": "Internship updated successfully",
        "internship": internship.to_dict()
    }), 200


# 5. Delete an internship
@internship_bp.route("/<int:internship_id>", methods=["DELETE"])
def delete_internship(internship_id):
    internship = db.session.get(Internship, internship_id)

    if internship is None:
        return jsonify({"error": "Internship not found"}), 404

    db.session.delete(internship)
    db.session.commit()

    return jsonify({
        "message": "Internship deleted successfully"
    }), 200


# 6. Search and filter internships
@internship_bp.route("/search", methods=["GET"])
def search_internships():

    query = Internship.query.join(Company)

    # General keyword search
    keyword = request.args.get("q", "").strip()

    if keyword:
        search_term = f"%{keyword}%"

        query = query.filter(
            or_(
                Internship.title.ilike(search_term),
                Internship.description.ilike(search_term),
                Internship.skills_required.ilike(search_term),
                Company.name.ilike(search_term)
            )
        )

    # Filter by internship title
    title = request.args.get("title", "").strip()

    if title:
        query = query.filter(
            Internship.title.ilike(f"%{title}%")
        )

    # Filter by company
    company = request.args.get("company", "").strip()

    if company:
        query = query.filter(
            Company.name.ilike(f"%{company}%")
        )

    # Filter by required skill
    skill = request.args.get("skill", "").strip()

    if skill:
        query = query.filter(
            Internship.skills_required.ilike(f"%{skill}%")
        )

    # Filter by location
    location = request.args.get("location", "").strip()

    if location:
        query = query.filter(
            Internship.location.ilike(f"%{location}%")
        )

    # Filter by work mode
    work_mode = request.args.get("work_mode", "").strip()

    if work_mode:
        query = query.filter(
            Internship.work_mode.ilike(f"%{work_mode}%")
        )

    # Filter by duration
    duration = request.args.get("duration", "").strip()

    if duration:
        query = query.filter(
            Internship.duration.ilike(f"%{duration}%")
        )

    # Filter by stipend keyword
    stipend = request.args.get("stipend", "").strip()

    if stipend:
        query = query.filter(
            Internship.stipend.ilike(f"%{stipend}%")
        )

    # Filter by minimum and maximum stipend
    min_stipend = request.args.get("min_stipend")
    max_stipend = request.args.get("max_stipend")

    try:
        if min_stipend:
            query = query.filter(
                cast(Internship.stipend, Float) >= float(min_stipend)
            )

        if max_stipend:
            query = query.filter(
                cast(Internship.stipend, Float) <= float(max_stipend)
            )

    except ValueError:
        return jsonify({
            "error": "Stipend filters must be numeric"
        }), 400

    internships = query.all()

    return jsonify({
        "count": len(internships),
        "internships": [
            internship.to_dict() for internship in internships
        ]
    }), 200
