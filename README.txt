INTERNTRACK — UPGRADED INTERNSHIP PORTAL

FEATURES
- Company directory: add/edit/delete companies and maintain website, location, industry, roles, skills, eligibility, CGPA, vacancies, hiring status, selection process and deadline.
- Company cards show applicant and selected/hired counts calculated from application records.
- Company detail view and Apply Now. Applications are automatically added to My Applications.
- Application status tracking and CSV export.
- Monthly interview calendar, interview rounds, meeting links and upcoming reminders.
- Offer records, received/accepted/declined status and offer totals.
- Student email composer and email activity log.
- SQLite database with safe additions for the previous app database schema.

RUN ON WINDOWS
1. Extract this ZIP.
2. Open the folder containing app.py in VS Code.
3. Open Terminal > New Terminal.
4. Run:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
5. Open http://127.0.0.1:5000 for the company homepage.\n6. Open http://127.0.0.1:5000/dashboard for applications, interviews, offers, reminders and email.

IMPORTANT — EMAIL CONFIGURATION
The email page is included, but real sending needs an SMTP account and app password.
In PowerShell, set these variables before starting the app (replace the example values):
  $env:SMTP_HOST="smtp.gmail.com"
  $env:SMTP_PORT="587"
  $env:SMTP_USER="your-email@gmail.com"
  $env:SMTP_PASSWORD="your-16-character-app-password"
  $env:SMTP_FROM="your-email@gmail.com"
Then run: python app.py
For Gmail, use a Google App Password with 2-Step Verification. Never put your password directly in source code or share it.

DATA / HONEST COUNTS
The included companies.db preserves the 10 company records from your uploaded database. Add or edit company details and record actual student applications, selection statuses and offers. Applicant/hired/offer totals are calculated from those saved records; the project does not invent hiring statistics. "Hired" is counted as applications with status Selected.
This version is a local single-student demo (student_id=1), not a multi-user production deployment. The company directory is shared in this local app, while My Applications is a demo student workspace. Before deployment, add login/roles, per-student authorization, CSRF protection, secure secret storage, HTTPS, validation, backups and production hosting. Do not use debug mode in production.
\nINTEGRATED USER FILES\n- The original companies.html and company_details.html are used as the public company pages.\n- Existing company database records are preserved; extra fields are added automatically on first startup.\n- Company pages show application/hired counts and include an Apply Now form.\n