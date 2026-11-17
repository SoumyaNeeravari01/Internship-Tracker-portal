
from app.extensions import db


class Internship(db.Model):
    __tablename__ = "internships"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False
    )

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    skills_required = db.Column(db.Text)
    location = db.Column(db.String(150))
    stipend = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    work_mode = db.Column(db.String(50))
    eligibility = db.Column(db.Text)
    deadline = db.Column(db.String(50))
    application_url = db.Column(db.String(255))

    # Connect Internship to Company
    company = db.relationship(
        "Company",
        back_populates="internships"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "title": self.title,
            "description": self.description,
            "skills_required": self.skills_required,
            "location": self.location,
            "stipend": self.stipend,
            "duration": self.duration,
            "work_mode": self.work_mode,
            "eligibility": self.eligibility,
            "deadline": self.deadline,
            "application_url": self.application_url
        }
