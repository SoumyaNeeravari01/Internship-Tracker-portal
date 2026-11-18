from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from database import init_db, get_db_connection
from tracking.routes import tracking_bp
from tracking.analytics import analytics_bp
from tracking.export import export_bp
from datetime import date

app = Flask(__name__)
app.secret_key = "change-this-before-deployment"
app.config["JSON_SORT_KEYS"] = False
app.register_blueprint(tracking_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(export_bp)

def list_companies():
    q = request.args.get("q", "").strip()
    industry = request.args.get("industry", "").strip()
    location = request.args.get("location", "").strip()
    sql = """SELECT co.*,
      (SELECT COUNT(*) FROM applications a WHERE a.company_id=co.id) AS applicants,
      (SELECT COUNT(*) FROM applications a WHERE a.company_id=co.id AND a.status='Selected') AS hired
      FROM companies co WHERE 1=1"""
    params = []
    if q:
        sql += " AND (co.name LIKE ? OR co.technologies LIKE ? OR co.roles LIKE ? OR co.industry LIKE ?)"
        params += [f"%{q}%"] * 4
    if industry:
        sql += " AND co.industry = ?"; params.append(industry)
    if location:
        sql += " AND co.location LIKE ?"; params.append(f"%{location}%")
    sql += " ORDER BY co.name"
    with get_db_connection() as c:
        return c.execute(sql, params).fetchall()

@app.route("/")
def home():
    return render_template("companies.html", companies=list_companies())

@app.route("/companies")
def explore_companies():
    return render_template("companies.html", companies=list_companies())

@app.route("/company/<int:company_id>")
def company_details(company_id):
    with get_db_connection() as c:
        company = c.execute("""SELECT co.*,
          (SELECT COUNT(*) FROM applications a WHERE a.company_id=co.id) applicants,
          (SELECT COUNT(*) FROM applications a WHERE a.company_id=co.id AND a.status='Selected') hired
          FROM companies co WHERE co.id=?""", (company_id,)).fetchone()
    if company is None:
        return "Company not found", 404
    return render_template("company_details.html", company=company)

@app.post("/apply")
def apply_from_profile():
    company_id = request.form.get("company_id", type=int)
    role = request.form.get("internship_role", "").strip()
    email = request.form.get("student_email", "").strip()
    notes = request.form.get("notes", "").strip()
    if not company_id or not role or not email:
        flash("Please provide your role and email before applying.")
        return redirect(request.referrer or url_for("home"))
    with get_db_connection() as c:
        company = c.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
        if not company:
            return "Company not found", 404
        if company["hiring_status"] == "Closed":
            flash("Applications for this company are closed.")
            return redirect(url_for("company_details", company_id=company_id))
        c.execute("""INSERT INTO applications
          (student_id,company_id,company_name,internship_role,application_date,deadline,notes,student_email)
          VALUES (1,?,?,?,?,?,?,?)""",
          (company_id, company["name"], role, date.today().isoformat(),
           company["deadline"], notes, email))
        app_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        c.execute("INSERT INTO status_history(application_id,new_status) VALUES(?,'Applied')", (app_id,))
    flash("Your application has been added to My Applications.")
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/health")
def health():
    return jsonify({"application": "InternTrack", "status": "running"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
