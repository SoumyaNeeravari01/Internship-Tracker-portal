
from app.extensions import db


class HiringProcess(db.Model):
    __tablename__ = "hiring_processes"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False,
        unique=True
    )

    hiring_stages = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    required_skills = db.Column(db.Text)
    required_documents = db.Column(db.Text)
    hiring_season = db.Column(db.String(100))
    official_link = db.Column(db.String(255))
    source_url = db.Column(db.String(255))
    verified_on = db.Column(db.String(50))

    company = db.relationship(
        "Company",
        back_populates="hiring_process"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "hiring_stages": self.hiring_stages,
            "eligibility": self.eligibility,
            "required_skills": self.required_skills,
            "required_documents": self.required_documents,
            "hiring_season": self.hiring_season,
            "official_link": self.official_link,
            "source_url": self.source_url,
            "verified_on": self.verified_on
        }
