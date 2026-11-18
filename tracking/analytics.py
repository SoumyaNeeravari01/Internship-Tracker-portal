from flask import Blueprint,jsonify
from database import get_db_connection
analytics_bp=Blueprint('analytics',__name__,url_prefix='/api')
@analytics_bp.get('/analytics')
def analytics():
    with get_db_connection() as c:
        total=c.execute("SELECT COUNT(*) FROM applications WHERE student_id=1").fetchone()[0]
        interviews=c.execute("SELECT COUNT(*) FROM interviews i JOIN applications a ON a.id=i.application_id WHERE a.student_id=1").fetchone()[0]
        offers=c.execute("SELECT COUNT(*) FROM offers o JOIN applications a ON a.id=o.application_id WHERE a.student_id=1").fetchone()[0]
        accepted=c.execute("SELECT COUNT(*) FROM offers o JOIN applications a ON a.id=o.application_id WHERE a.student_id=1 AND o.offer_status='Accepted'").fetchone()[0]
        rows=c.execute("SELECT status,COUNT(*) n FROM applications WHERE student_id=1 GROUP BY status").fetchall()
    return jsonify(total_applications=total,interviews=interviews,offers=offers,accepted_offers=accepted,
      selection_rate=round(accepted*100/total,1) if total else 0,by_status={r['status']:r['n'] for r in rows})
