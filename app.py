from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)
app.secret_key = 'campus_secret_key_123'

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('home.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = generate_password_hash(request.form['password'])
        dept     = request.form['department']
        year     = request.form['year']

        cur = mysql.connection.cursor()
        # Insert into users
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'student')",
                    (name, email, password))
        user_id = cur.lastrowid
        # Insert into students
        cur.execute("INSERT INTO students (user_id, department, year) VALUES (%s, %s, %s)",
                    (user_id, dept, year))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id']   = user[0]
            session['user_name'] = user[1]
            session['role']      = user[4]
            if user[4] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# ---------- STUDENT DASHBOARD ----------
@app.route('/dashboard')
def student_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['user_name'])
# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- SUBMIT ISSUE ----------
@app.route('/submit', methods=['GET', 'POST'])
def submit_issue():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category    = request.form['category']
        description = request.form['description']
        location    = request.form['location']
        req_type    = request.form['request_type']
        priority    = request.form['priority']
        photo_name  = None

        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                photo_name = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_name))

        cur = mysql.connection.cursor()

        # Get student_id from session user_id
        cur.execute("SELECT student_id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cur.fetchone()
        student_id = student[0]

        # Insert into requests
        cur.execute("""
            INSERT INTO requests (student_id, request_type, description, status, priority)
            VALUES (%s, %s, %s, 'pending', %s)
        """, (student_id, req_type, description, priority))
        request_id = cur.lastrowid

        # Insert into issue_requests or service_requests
        if req_type == 'maintenance':
            cur.execute("""
                INSERT INTO issue_requests (request_id, location, severity)
                VALUES (%s, %s, %s)
            """, (request_id, location, priority))
        else:
            cur.execute("""
                INSERT INTO service_requests (request_id, service_type, department)
                VALUES (%s, %s, %s)
            """, (request_id, category, location))

        mysql.connection.commit()
        cur.close()
        flash('Your request has been submitted successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('submit.html')

# ---------- MY REQUESTS ----------
@app.route('/my-requests')
def my_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.request_id, r.request_type, r.description, r.status,
               r.priority, r.created_date, r.estimated_completion
        FROM requests r
        JOIN students s ON r.student_id = s.student_id
        WHERE s.user_id = %s
        ORDER BY r.created_date DESC
    """, (session['user_id'],))
    requests_list = cur.fetchall()
    cur.close()
    return render_template('my_requests.html', requests=requests_list)

# ---------- ADMIN DASHBOARD ----------
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    status_filter = request.args.get('status')
    cur = mysql.connection.cursor()

    # Get stats
    cur.execute("SELECT COUNT(*) FROM requests")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM requests WHERE status='pending'")
    pending = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM requests WHERE status='in_progress'")
    in_progress = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM requests WHERE status='resolved'")
    resolved = cur.fetchone()[0]

    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved
    }

    # Get requests with student name
    if status_filter:
        cur.execute("""
            SELECT r.request_id, u.name, r.request_type, r.description,
                   r.priority, r.status, r.created_date, r.estimated_completion
            FROM requests r
            JOIN students s ON r.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            WHERE r.status = %s
            ORDER BY r.created_date DESC
        """, (status_filter,))
    else:
        cur.execute("""
            SELECT r.request_id, u.name, r.request_type, r.description,
                   r.priority, r.status, r.created_date, r.estimated_completion
            FROM requests r
            JOIN students s ON r.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            ORDER BY r.created_date DESC
        """)

    requests_list = cur.fetchall()
    cur.close()
    return render_template('admin_dashboard.html', requests=requests_list, stats=stats)


# ---------- MANAGE SINGLE REQUEST ----------
@app.route('/admin/request/<int:request_id>', methods=['GET', 'POST'])
def manage_request(request_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        status               = request.form['status']
        estimated_completion = request.form['estimated_completion'] or None
        notes                = request.form['notes']

        # Update request
        cur.execute("""
            UPDATE requests
            SET status=%s, estimated_completion=%s
            WHERE request_id=%s
        """, (status, estimated_completion, request_id))

        # Save notification for student
        cur.execute("""
            SELECT s.user_id FROM requests r
            JOIN students s ON r.student_id = s.student_id
            WHERE r.request_id = %s
        """, (request_id,))
        student = cur.fetchone()
        if student and notes:
            cur.execute("""
                INSERT INTO notifications (user_id, message)
                VALUES (%s, %s)
            """, (student[0], notes))

        # Log status change in request_history
        cur.execute("""
            INSERT INTO request_history (request_id, new_status)
            VALUES (%s, %s)
        """, (request_id, status))

        mysql.connection.commit()
        cur.close()
        flash('Request updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # GET — fetch request details
    cur.execute("""
        SELECT r.request_id, u.name, r.request_type, r.description,
               r.priority, r.status, r.created_date, r.estimated_completion
        FROM requests r
        JOIN students s ON r.student_id = s.student_id
        JOIN users u ON s.user_id = u.user_id
        WHERE r.request_id = %s
    """, (request_id,))
    r = cur.fetchone()
    cur.close()
    return render_template('manage_request.html', r=r)


# ---------- OFFICE COUNTERS ----------
@app.route('/counters')
def office_counters():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM office_counters")
    counters = cur.fetchall()
    cur.close()
    return render_template('office_counters.html', counters=counters)

# ---------- NOTIFICATIONS ----------
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT notification_id, message, sent_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY sent_at DESC
    """, (session['user_id'],))
    notifs = cur.fetchall()
    cur.close()
    return render_template('notifications.html', notifs=notifs)


# ---------- ADMIN REPORTS ----------
@app.route('/admin/reports')
def admin_reports():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Requests by status
    cur.execute("""
        SELECT status, COUNT(*) as count
        FROM requests
        GROUP BY status
    """)
    by_status = cur.fetchall()

    # Requests by type
    cur.execute("""
        SELECT request_type, COUNT(*) as count
        FROM requests
        GROUP BY request_type
    """)
    by_type = cur.fetchall()

    # Requests by priority
    cur.execute("""
        SELECT priority, COUNT(*) as count
        FROM requests
        GROUP BY priority
    """)
    by_priority = cur.fetchall()

    # Recent requests per day (last 7 days)
    cur.execute("""
        SELECT DATE(created_date) as day, COUNT(*) as count
        FROM requests
        WHERE created_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(created_date)
        ORDER BY day ASC
    """)
    by_day = cur.fetchall()

    cur.close()
    return render_template('reports.html',
        by_status=by_status,
        by_type=by_type,
        by_priority=by_priority,
        by_day=by_day
    )


# ---------- ADMIN COUNTERS MANAGEMENT ----------
@app.route('/admin/counters', methods=['GET', 'POST'])
def admin_counters():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        counter_id = request.form['counter_id']
        status     = request.form['status']
        queue      = request.form['queue_length']
        cur.execute("""
            UPDATE office_counters
            SET status=%s, queue_length=%s
            WHERE counter_id=%s
        """, (status, queue, counter_id))
        mysql.connection.commit()
        flash('Counter updated!', 'success')

    cur.execute("SELECT * FROM office_counters")
    counters = cur.fetchall()
    cur.close()
    return render_template('admin_counters.html', counters=counters)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))