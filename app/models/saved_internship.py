
from app.extensions import db


class SavedInternship(db.Model):
    __tablename__ = "saved_internships"

    id = db.Column(db.Integer, primary_key=True)

    # Student ID will connect to Siri's Users table later
    user_id = db.Column(db.Integer, nullable=False)

    internship_id = db.Column(
        db.Integer,
        db.ForeignKey("internships.id"),
        nullable=False
    )

    saved_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    internship = db.relationship(
        "Internship",
        backref=db.backref("saved_by_users", lazy=True)
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "internship_id",
            name="unique_saved_internship"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "internship_id": self.internship_id,
            "saved_at": self.saved_at.isoformat() if self.saved_at else None,
            "internship": self.internship.to_dict()
        }
