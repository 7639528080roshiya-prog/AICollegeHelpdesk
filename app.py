from flask import Flask, render_template, request, redirect, jsonify, session
import os
app = Flask(__name__)
app.secret_key = "gct_final_both_pass"
os.makedirs('staff_files', exist_ok=True)

DATA = {
  'college name': 'Government College of Technology, Coimbatore',
  'principal': 'Dr. K. Manonmani, M.E., Ph.D', 'contact': '0422-2432221',
  'location': 'Thadagam Road, Coimbatore', 'about': 'GCT - Govt College since 1945.',
  'ug_courses': 'B.E CSE, ECE, Mechanical, Civil, EEE', 'pg_courses': 'M.E CSE, MBA, MCA',
  'timing': '8:30 AM to 4:30 PM', 'facilities': 'Library, Hostel, Labs', 'hostel': 'Hostel available'
}
STAFF_DATA = {
  "admission": "UG Admission 2026 open", "naan_mudhalvan": "Naan Mudhalvan Scheme - Skill Training",
  "exam_fees": "UG Rs.1500/sem, PG Rs.2000/sem", "announcement": "Welcome!",
  "students": {}, "results": {}, "staff_list": {}, "hod_list": {},
  "library_books": {
      "CSE001": {"title": "Python Programming", "author": "Guido", "dept": "CSE", "total": 10, "available": 10},
      "ECE002": {"title": "Digital Electronics", "author": "Morris Mano", "dept": "ECE", "total": 5, "available": 5},
      "MECH01": {"title": "Thermodynamics", "author": "Cengel", "dept": "Mechanical", "total": 8, "available": 8}
  },
  "game_results": [],
  "attendance": {},
  "fees_paid": {},
  "complaints": [],
  "placements": [],
  "events": []
}

STAFF_PASS = "staff123"
PRINCIPAL_PASS = "gct123"

@app.route('/')
def home(): return render_template('home.html', username=session.get('user','Guest'), data=DATA, staff_data=STAFF_DATA)
@app.route('/student')
def student(): return render_template('student.html', data=DATA, staff_data=STAFF_DATA)

@app.route('/staff', methods=['GET','POST'])
def staff():
    if request.method == 'POST':
        if request.form.get('password','').strip() == STAFF_PASS:
            session['is_staff'] = True
            return redirect('/staff')
        else:
            return f"<h3>Wrong Password staff123</h3><a href='/staff'>Try Again</a>"
    if not session.get('is_staff') and not session.get('is_principal'):
        return '''
        <body style="text-align:center;padding:50px;background:#e8f5e9">
        <h2>👨‍🏫 Staff Login</h2>
        <form method="POST"><input type="password" name="password" placeholder="Password" style="padding:12px;width:260px" required><br><br>
        <button style="padding:12px 30px;background:#4CAF50;color:white;border:none;border-radius:8px">Login</button></form>
        <p>Password: <b>staff123</b></p><a href="/">Home</a></body>
        '''
    return render_template('staff.html', data=DATA, staff_data=STAFF_DATA)

@app.route('/principal', methods=['GET','POST'])
def principal():
    if request.method == 'POST':
        if request.form.get('password','').strip() == PRINCIPAL_PASS:
            session['is_principal'] = True
            session['is_staff'] = True
            return redirect('/principal')
        else:
            return f"<h3>Wrong Password gct123</h3><a href='/principal'>Try Again</a>"
    if not session.get('is_principal'):
        return '''
        <body style="text-align:center;padding:50px;background:#ffebee">
        <h2>🔐 Principal Login</h2>
        <form method="POST"><input type="password" name="password" placeholder="Password" style="padding:12px;width:260px" required><br><br>
        <button style="padding:12px 30px;background:#d32f2f;color:white;border:none;border-radius:8px">Login</button></form>
        <p>Password: <b>gct123</b></p><a href="/">Home</a></body>
        '''
    return render_template('principal.html', data=DATA, staff_data=STAFF_DATA)

@app.route('/library')
def library(): return render_template('library.html', data=DATA, staff_data=STAFF_DATA)
@app.route('/games')
def games(): return render_template('games.html', data=DATA, staff_data=STAFF_DATA)

@app.route('/games/save', methods=['POST'])
def save_game_result():
    if not session.get('is_staff') and not session.get('is_principal'): return "Staff Only"
    STAFF_DATA['game_results'].append({
        "game": request.form.get('game',''), "winner": request.form.get('winner',''),
        "dept": request.form.get('dept','CSE'), "prize": request.form.get('prize','1st Prize')
    })
    return redirect('/principal' if session.get('is_principal') else '/staff')

@app.route('/attendance/save', methods=['POST'])
def save_attendance():
    if not session.get('is_staff') and not session.get('is_principal'): return "Staff Only"
    roll = request.form.get('roll','').upper().strip()
    STAFF_DATA['attendance'][roll] = request.form.get('percent','0')
    return redirect('/principal' if session.get('is_principal') else '/staff')

@app.route('/fees/save', methods=['POST'])
def save_fees():
    if not session.get('is_staff') and not session.get('is_principal'): return "Staff Only"
    roll = request.form.get('roll','').upper().strip()
    STAFF_DATA['fees_paid'][roll] = {"amount": request.form.get('amount',''), "status": request.form.get('status','Paid')}
    return redirect('/principal' if session.get('is_principal') else '/staff')

@app.route('/complaint', methods=['GET','POST'])
def complaint():
    if request.method == 'POST':
        STAFF_DATA['complaints'].append({"roll": request.form.get('roll','Anonymous'), "msg": request.form.get('msg','')})
        return "<h3>Complaint Sent! ✅ <a href='/'>Home</a></h3>"
    return render_template('complaint.html', staff_data=STAFF_DATA)

@app.route('/placement', methods=['GET','POST'])
def placement():
    if request.method == 'POST':
        if not session.get('is_staff') and not session.get('is_principal'): return "Staff Only"
        STAFF_DATA['placements'].append({"company": request.form.get('company',''), "package": request.form.get('package',''), "students": request.form.get('students','')})
        return redirect('/placement')
    return render_template('placement.html', staff_data=STAFF_DATA, data=DATA)

@app.route('/events', methods=['GET','POST'])
def events():
    if request.method == 'POST':
        if not session.get('is_principal'): return "Principal Only"
        STAFF_DATA['events'].append({"title": request.form.get('title',''), "date": request.form.get('date',''), "dept": request.form.get('dept','')})
        return redirect('/principal')
    return render_template('events.html', staff_data=STAFF_DATA, data=DATA)

@app.route('/logout')
def logout(): session.clear(); return redirect('/')
@app.route('/principal/logout')
def principal_logout(): session.clear(); return redirect('/')
@app.route('/staff/logout')
def staff_logout(): session.clear(); return redirect('/')

@app.route('/staff/upload', methods=['POST'])
def staff_upload():
    typ = request.form.get('type')
    if typ in ['admission','naan_mudhalvan','exam_fees','exam_result']:
        if not session.get('is_staff') and not session.get('is_principal'): return "Access Denied"
    else:
        if not session.get('is_principal'): return "<h3>Principal ku mattum! <a href='/principal'>Login</a></h3>"
    if typ == 'admission': STAFF_DATA['admission'] = request.form.get('text','')
    elif typ == 'naan_mudhalvan': STAFF_DATA['naan_mudhalvan'] = request.form.get('text','')
    elif typ == 'exam_fees': STAFF_DATA['exam_fees'] = request.form.get('text','')
    elif typ == 'exam_result':
        roll = request.form.get('roll','').strip().upper()
        STAFF_DATA['results'][roll] = {'cgpa': request.form.get('cgpa',''),'result': request.form.get('result',''),'dept': request.form.get('dept','CSE')}
    elif typ == 'staff_details':
        sid = request.form.get('staff_id','').strip().upper()
        STAFF_DATA['staff_list'][sid] = {'name': request.form.get('name',''),'dept': request.form.get('dept','CSE'),'designation': request.form.get('designation','')}
    elif typ == 'hod_details':
        STAFF_DATA['hod_list'][request.form.get('dept','CSE')] = {'name': request.form.get('name',''),'exp': request.form.get('exp',''),'contact': request.form.get('contact','')}
    elif typ == 'student_details':
        roll = request.form.get('roll','').strip().upper()
        STAFF_DATA['students'][roll] = {'name': request.form.get('name',''),'dept': request.form.get('dept','CSE'),'year': request.form.get('year','')}
    return redirect('/principal' if session.get('is_principal') else '/staff')

@app.route('/get_result', methods=['POST'])
def get_result():
    roll = request.form.get('roll','').strip().upper()
    res = STAFF_DATA['results'].get(roll)
    if res: return jsonify({"found": True, "roll": roll, "data": res, "student": STAFF_DATA['students'].get(roll)})
    else: return jsonify({"found": False})

@app.route('/chatbot')
def chatbot(): return render_template('index.html', username='admin')
@app.route('/login')
def login(): return redirect('/')
@app.route('/language', methods=['GET','POST'])
def language(): return render_template('language.html')

# --- LIVE CHATBOX UPDATED ---
@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message','').lower()
    reply = "Theriyala da, vera maathiri kelu - Admission, Fees, Library, Games, Placement, Contact nu kelu da!"
    if 'principal' in user_msg: reply = f"Principal: {DATA['principal']} da"
    elif 'admission' in user_msg: reply = f"{STAFF_DATA['admission']} - Contact {DATA['contact']}"
    elif 'fees' in user_msg: reply = f"Fees Details: {STAFF_DATA['exam_fees']} da"
    elif 'library' in user_msg: reply = f"Library la {len(STAFF_DATA['library_books'])} books irukku! /library poi full list paaru da!"
    elif 'game' in user_msg or 'sports' in user_msg: reply = f"Sports la {len(STAFF_DATA['game_results'])} results saved! Winner lam /games la paaru!"
    elif 'placement' in user_msg: reply = f"Placement la {len(STAFF_DATA['placements'])} company vanthirukku - /placement la paaru da!"
    elif 'attendance' in user_msg: reply = "Attendance staff / principal than save pannuvanga da"
    elif 'contact' in user_msg or 'phone' in user_msg: reply = f"Contact: {DATA['contact']} - {DATA['location']} da"
    elif 'course' in user_msg or 'dept' in user_msg: reply = f"UG: {DATA['ug_courses']} | PG: {DATA['pg_courses']}"
    elif 'hostel' in user_msg: reply = DATA['hostel']
    elif 'hi' in user_msg or 'hello' in user_msg or 'vanakkam' in user_msg or 'da' in user_msg: reply = "Vanakkam da! 🙏 Naan GCT Live Chatbot da! Admission, Fees, Library, Games, Placement ethu venalum kelu!"
    return jsonify({"reply": reply})

if __name__=='__main__': app.run(debug=True)