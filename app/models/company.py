
from app.extensions import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    careers_page = db.Column(db.String(255))
    location = db.Column(db.String(150))
    logo_url = db.Column(db.String(255))

    # One company can have multiple internships
    internships = db.relationship(
        "Internship",
        back_populates="company",
        lazy=True
    )

    # One company has one hiring process
    hiring_process = db.relationship(
        "HiringProcess",
        back_populates="company",
        uselist=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "description": self.description,
            "website": self.website,
            "careers_page": self.careers_page,
            "location": self.location,
            "logo_url": self.logo_url
        }
