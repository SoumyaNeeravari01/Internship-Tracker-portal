from flask import Blueprint,request,jsonify
from database import get_db_connection
from datetime import date
import os,smtplib
from email.message import EmailMessage
tracking_bp=Blueprint('tracking',__name__,url_prefix='/api')
STATUSES=['Applied','Under Review','Shortlisted','Interview Scheduled','Selected','Rejected','Withdrawn']
def err(msg,code=400): return jsonify(error=msg),code
@tracking_bp.get('/companies')
def companies():
    q=request.args.get('q','').strip()
    with get_db_connection() as c:
        rows=c.execute("""SELECT co.*,
          (SELECT COUNT(*) FROM applications a WHERE a.company_id=co.id) applicants,
          (SELECT COUNT(*) FROM applications a WHERE a.company_id=co.id AND a.status='Selected') hired
          FROM companies co WHERE co.name LIKE ? OR co.roles LIKE ? ORDER BY co.name""",(f'%{q}%',f'%{q}%')).fetchall()
    return jsonify([dict(x) for x in rows])
@tracking_bp.post('/companies')
def add_company():
    d=request.get_json(silent=True) or {}
    if not d.get('name','').strip(): return err('Company name is required.')
    allowed=['name','website','location','industry','description','roles','skills','eligibility','min_cgpa','hiring_status','vacancies','deadline','selection_process']
    vals=[d.get(k,'') for k in allowed]
    with get_db_connection() as c:
        cur=c.execute(f"INSERT INTO companies ({','.join(allowed)}) VALUES ({','.join(['?']*len(allowed))})",vals)
    return jsonify(message='Company added.',id=cur.lastrowid),201
@tracking_bp.put('/companies/<int:cid>')
def edit_company(cid):
    d=request.get_json(silent=True) or {}
    allowed=['name','website','location','industry','description','roles','skills','eligibility','min_cgpa','hiring_status','vacancies','deadline','selection_process']
    upd={k:d[k] for k in allowed if k in d}
    if not upd:return err('No company details supplied.')
    with get_db_connection() as c:
        cur=c.execute('UPDATE companies SET '+','.join(k+'=?' for k in upd)+' WHERE id=?',[*upd.values(),cid])
    if not cur.rowcount:return err('Company not found.',404)
    return jsonify(message='Company updated.')
@tracking_bp.delete('/companies/<int:cid>')
def delete_company(cid):
    with get_db_connection() as c:
        cur=c.execute('DELETE FROM companies WHERE id=?',(cid,))
    if not cur.rowcount:return err('Company not found.',404)
    return jsonify(message='Company deleted.')
@tracking_bp.get('/applications')
def applications():
    with get_db_connection() as c:
        rows=c.execute("SELECT * FROM applications WHERE student_id=1 ORDER BY created_at DESC,id DESC").fetchall()
    return jsonify([dict(r) for r in rows])
@tracking_bp.post('/applications')
def apply():
    d=request.get_json(silent=True) or {}
    if (not d.get('company_id') and not d.get('company_name')) or not d.get('internship_role'):return err('Company and internship role are required.')
    applied=d.get('application_date') or date.today().isoformat()
    with get_db_connection() as c:
        if d.get('company_id'):
            co=c.execute('SELECT * FROM companies WHERE id=?',(d['company_id'],)).fetchone()
            if not co:return err('Company not found.',404)
            name=co['name']; deadline=d.get('deadline') or co['deadline']
        else:name=d['company_name'];deadline=d.get('deadline')
        cur=c.execute("""INSERT INTO applications(student_id,company_id,company_name,internship_role,application_date,deadline,notes,student_email)
          VALUES(1,?,?,?,?,?,?,?)""",(d.get('company_id'),name,d['internship_role'],applied,deadline,d.get('notes',''),d.get('student_email','')))
        c.execute("INSERT INTO status_history(application_id,new_status) VALUES(?,'Applied')",(cur.lastrowid,))
    return jsonify(message='Application submitted.',id=cur.lastrowid),201
@tracking_bp.patch('/applications/<int:aid>/status')
def status(aid):
    d=request.get_json(silent=True) or {}; st=d.get('status')
    if st not in STATUSES:return err('Invalid status.')
    with get_db_connection() as c:
        row=c.execute('SELECT status FROM applications WHERE id=? AND student_id=1',(aid,)).fetchone()
        if not row:return err('Application not found.',404)
        c.execute('UPDATE applications SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(st,aid))
        c.execute('INSERT INTO status_history(application_id,old_status,new_status) VALUES(?,?,?)',(aid,row['status'],st))
    return jsonify(message='Status updated.')
@tracking_bp.delete('/applications/<int:aid>')
def delete_app(aid):
    with get_db_connection() as c: cur=c.execute('DELETE FROM applications WHERE id=? AND student_id=1',(aid,))
    if not cur.rowcount:return err('Application not found.',404)
    return jsonify(message='Application deleted.')
@tracking_bp.get('/interviews')
def interviews():
    with get_db_connection() as c:
        rows=c.execute("SELECT i.*,a.company_name,a.internship_role FROM interviews i JOIN applications a ON a.id=i.application_id WHERE a.student_id=1 ORDER BY i.interview_date,i.interview_time").fetchall()
    return jsonify([dict(r) for r in rows])
@tracking_bp.post('/interviews')
def add_interview():
    d=request.get_json(silent=True) or {}
    if not d.get('application_id') or not d.get('interview_date'):return err('Choose an application and interview date.')
    with get_db_connection() as c:
        a=c.execute('SELECT id FROM applications WHERE id=? AND student_id=1',(d['application_id'],)).fetchone()
        if not a:return err('Application not found.',404)
        cur=c.execute("INSERT INTO interviews(application_id,interview_date,interview_time,interview_round,meeting_link,notes) VALUES(?,?,?,?,?,?)",
          (d['application_id'],d['interview_date'],d.get('interview_time',''),d.get('interview_round','First Round'),d.get('meeting_link',''),d.get('notes','')))
        c.execute("UPDATE applications SET status='Interview Scheduled' WHERE id=?",(d['application_id'],))
    return jsonify(message='Interview scheduled.',id=cur.lastrowid),201
@tracking_bp.delete('/interviews/<int:iid>')
def delete_interview(iid):
    with get_db_connection() as c:
        cur=c.execute("DELETE FROM interviews WHERE id=? AND application_id IN (SELECT id FROM applications WHERE student_id=1)",(iid,))
    if not cur.rowcount:return err('Interview not found.',404)
    return jsonify(message='Interview removed.')
@tracking_bp.get('/offers')
def offers():
    with get_db_connection() as c:
        rows=c.execute("SELECT o.*,a.company_name,a.internship_role FROM offers o JOIN applications a ON a.id=o.application_id WHERE a.student_id=1 ORDER BY o.id DESC").fetchall()
    return jsonify([dict(r) for r in rows])
@tracking_bp.post('/offers')
def add_offer():
    d=request.get_json(silent=True) or {}
    if not d.get('application_id'):return err('Select an application.')
    with get_db_connection() as c:
        try:
            cur=c.execute("INSERT INTO offers(application_id,offer_date,joining_date,stipend,offer_status,notes) SELECT id,?,?,?,?,? FROM applications WHERE id=? AND student_id=1",
              (d.get('offer_date'),d.get('joining_date'),float(d.get('stipend') or 0),d.get('offer_status','Received'),d.get('notes',''),d['application_id']))
        except Exception:return err('An offer already exists for this application, or the data is invalid.')
        if not cur.rowcount:return err('Application not found.',404)
        if d.get('offer_status')=='Accepted':c.execute("UPDATE applications SET status='Selected' WHERE id=?",(d['application_id'],))
    return jsonify(message='Offer recorded.'),201
@tracking_bp.patch('/offers/<int:oid>')
def update_offer(oid):
    d=request.get_json(silent=True) or {}; st=d.get('offer_status')
    if st not in ['Received','Accepted','Declined']:return err('Invalid offer status.')
    with get_db_connection() as c:
        cur=c.execute("UPDATE offers SET offer_status=? WHERE id=? AND application_id IN (SELECT id FROM applications WHERE student_id=1)",(st,oid))
    if not cur.rowcount:return err('Offer not found.',404)
    return jsonify(message='Offer updated.')
@tracking_bp.get('/reminders')
def reminders():
    with get_db_connection() as c:
        ds=c.execute("SELECT id,company_name,internship_role,deadline,status FROM applications WHERE student_id=1 AND deadline IS NOT NULL AND deadline>=date('now') ORDER BY deadline").fetchall()
        ints=c.execute("SELECT i.id,i.interview_date,i.interview_time,i.interview_round,a.company_name,a.internship_role FROM interviews i JOIN applications a ON a.id=i.application_id WHERE a.student_id=1 AND i.interview_date>=date('now') ORDER BY i.interview_date,i.interview_time").fetchall()
    return jsonify(deadlines=[dict(x) for x in ds],interviews=[dict(x) for x in ints])
@tracking_bp.post('/email')
def send_email():
    d=request.get_json(silent=True) or {}; to=d.get('to','').strip(); subject=d.get('subject','').strip(); body=d.get('message','').strip()
    if not to or not subject or not body:return err('Recipient, subject and message are required.')
    host=os.getenv('SMTP_HOST'); user=os.getenv('SMTP_USER'); password=os.getenv('SMTP_PASSWORD')
    if not all([host,user,password]):return err('Email is not configured yet. Add SMTP_HOST, SMTP_USER, SMTP_PASSWORD and SMTP_PORT environment variables, then restart the app.',503)
    try:
        msg=EmailMessage();msg['From']=os.getenv('SMTP_FROM',user);msg['To']=to;msg['Subject']=subject;msg.set_content(body)
        with smtplib.SMTP(host,int(os.getenv('SMTP_PORT','587'))) as server:
            server.starttls();server.login(user,password);server.send_message(msg)
        result='Sent'
    except Exception as e: result='Failed: '+str(e)
    with get_db_connection() as c:c.execute('INSERT INTO email_log(recipient,subject,message,result) VALUES(?,?,?,?)',(to,subject,body,result))
    if result!='Sent':return err('Email could not be sent. Check SMTP settings.',502)
    return jsonify(message='Email sent successfully.')
@tracking_bp.get('/email-log')
def email_log():
    with get_db_connection() as c: rows=c.execute('SELECT recipient,subject,result,sent_at FROM email_log ORDER BY id DESC LIMIT 50').fetchall()
    return jsonify([dict(x) for x in rows])
