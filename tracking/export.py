import csv,io
from flask import Blueprint,Response
from database import get_db_connection
export_bp=Blueprint('export',__name__,url_prefix='/api')
@export_bp.get('/export')
def export_csv():
    out=io.StringIO(); w=csv.writer(out)
    w.writerow(['Company','Role','Applied','Deadline','Status','Student email'])
    with get_db_connection() as c:
        for r in c.execute("SELECT company_name,internship_role,application_date,deadline,status,student_email FROM applications WHERE student_id=1 ORDER BY id DESC"):
            w.writerow(list(r))
    return Response('\ufeff'+out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=interntrack_applications.csv'})
