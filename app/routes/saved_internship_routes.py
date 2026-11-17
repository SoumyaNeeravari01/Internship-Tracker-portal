
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.saved_internship import SavedInternship
from app.models.internship import Internship

saved_bp = Blueprint("saved_internships", __name__)


# 1. Save an internship
@saved_bp.route("/", methods=["POST"])
def save_internship():
    data = request.get_json(silent=True)

    if not data or not data.get("user_id") or not data.get("internship_id"):
        return jsonify({
            "error": "User ID and Internship ID are required"
        }), 400

    user_id = data["user_id"]
    internship_id = data["internship_id"]

    internship = db.session.get(Internship, internship_id)

    if internship is None:
        return jsonify({"error": "Internship not found"}), 404

    saved = SavedInternship.query.filter_by(
        user_id=user_id,
        internship_id=internship_id
    ).first()

    if saved:
        return jsonify({
            "message": "Internship is already saved"
        }), 409

    saved = SavedInternship(
        user_id=user_id,
        internship_id=internship_id
    )

    db.session.add(saved)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Internship is already saved"
        }), 409

    return jsonify({
        "message": "Internship saved successfully",
        "saved_internship": saved.to_dict()
    }), 201


# 2. View saved internships
@saved_bp.route("/", methods=["GET"])
def get_saved_internships():
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    saved_list = SavedInternship.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify({
        "count": len(saved_list),
        "saved_internships": [
            saved.to_dict() for saved in saved_list
        ]
    }), 200


# 3. Remove a saved internship
@saved_bp.route("/<int:saved_id>", methods=["DELETE"])
def remove_saved_internship(saved_id):
    saved = db.session.get(SavedInternship, saved_id)

    if saved is None:
        return jsonify({"error": "Saved internship not found"}), 404

    db.session.delete(saved)
    db.session.commit()

    return jsonify({
        "message": "Saved internship removed successfully"
    }), 200
