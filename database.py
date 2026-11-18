import sqlite3
from pathlib import Path

# Keep the uploaded company directory and its 10 existing records.
DATABASE = Path(__file__).with_name("companies.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with get_db_connection() as c:
        # Create the full company table for a new installation.
        c.execute("""
        CREATE TABLE IF NOT EXISTS companies(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          industry TEXT DEFAULT '', location TEXT DEFAULT '', description TEXT DEFAULT '',
          technologies TEXT DEFAULT '', website TEXT DEFAULT '', careers_url TEXT DEFAULT '',
          internship_roles TEXT DEFAULT ''
        )""")
        # Add the enhanced fields without deleting or replacing existing company data.
        cols = {r["name"] for r in c.execute("PRAGMA table_info(companies)")}
        additions = {
          "roles": "TEXT DEFAULT ''", "skills": "TEXT DEFAULT ''",
          "eligibility": "TEXT DEFAULT ''", "min_cgpa": "TEXT DEFAULT ''",
          "hiring_status": "TEXT DEFAULT 'Open'", "vacancies": "INTEGER DEFAULT 0",
          "deadline": "TEXT", "selection_process": "TEXT DEFAULT ''"
        }
        for name, decl in additions.items():
            if name not in cols:
                c.execute(f"ALTER TABLE companies ADD COLUMN {name} {decl}")
        # Copy values from the original columns into the new fields once.
        c.execute("""UPDATE companies SET
          roles=CASE WHEN COALESCE(roles,'')='' THEN COALESCE(internship_roles,'') ELSE roles END,
          skills=CASE WHEN COALESCE(skills,'')='' THEN COALESCE(technologies,'') ELSE skills END
        """)
        c.executescript("""
        CREATE TABLE IF NOT EXISTS applications(
          id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL DEFAULT 1,
          company_id INTEGER, company_name TEXT NOT NULL, internship_role TEXT NOT NULL,
          application_date TEXT NOT NULL, deadline TEXT, status TEXT NOT NULL DEFAULT 'Applied',
          notes TEXT DEFAULT '', student_email TEXT DEFAULT '',
          created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS interviews(
          id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER NOT NULL,
          interview_date TEXT NOT NULL, interview_time TEXT DEFAULT '',
          interview_round TEXT DEFAULT 'First Round', meeting_link TEXT DEFAULT '', notes TEXT DEFAULT '',
          FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS offers(
          id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER NOT NULL UNIQUE,
          offer_date TEXT, joining_date TEXT, stipend REAL DEFAULT 0,
          offer_status TEXT NOT NULL DEFAULT 'Received', notes TEXT DEFAULT '',
          FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS status_history(
          id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER NOT NULL,
          old_status TEXT, new_status TEXT NOT NULL, changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS email_log(
          id INTEGER PRIMARY KEY AUTOINCREMENT, recipient TEXT NOT NULL, subject TEXT NOT NULL,
          message TEXT NOT NULL, sent_at TEXT DEFAULT CURRENT_TIMESTAMP, result TEXT NOT NULL
        );
        """)
        app_cols = {r["name"] for r in c.execute("PRAGMA table_info(applications)")}
        for name, decl in [("company_id", "INTEGER"), ("student_email", "TEXT DEFAULT ''")]:
            if name not in app_cols:
                c.execute(f"ALTER TABLE applications ADD COLUMN {name} {decl}")
