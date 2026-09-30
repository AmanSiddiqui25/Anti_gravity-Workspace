import os
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ecoclean_super_secret_session_key_2026')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
db.init_db()
db.seed_data_if_empty()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- PAGE ROUTES ----------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login_page', role='user'))
    return render_template('user_dashboard.html', user_id=session.get('user_id'))

@app.route('/collector/dashboard')
def collector_dashboard():
    if session.get('role') != 'collector':
        return redirect(url_for('login_page', role='collector'))
    return render_template('collector_dashboard.html', collector_id=session.get('collector_id'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login_page', role='admin'))
    return render_template('admin_dashboard.html')

# ----------------- AUTHENTICATION APIS ----------------- #

@app.route('/api/register/user', methods=['POST'])
def register_user():
    data = request.form if request.form else request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    age = data.get('age')
    area = data.get('area', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    gender = data.get('gender', '').strip()
    password = data.get('password', '')

    if not (name and area and email and phone and password):
        return jsonify({'success': False, 'message': 'Please fill all required fields.'}), 400

    conn = db.get_db()
    cursor = conn.cursor()

    # Check unique email/phone
    cursor.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (email, phone))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email or phone number is already registered.'}), 400

    unique_id = db.generate_user_id()
    pwd_hash = generate_password_hash(password)

    cursor.execute('''
        INSERT INTO users (unique_id, name, age, area, email, phone, gender, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (unique_id, name, age, area, email, phone, gender, pwd_hash))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session['role'] = 'user'
    session['user_id'] = user_id
    session['unique_id'] = unique_id
    session['name'] = name

    return jsonify({
        'success': True,
        'message': f'Registration successful! Your Unique ID is {unique_id}',
        'redirect': '/user/dashboard'
    })

@app.route('/api/login/user', methods=['POST'])
def login_user():
    data = request.get_json(silent=True) or request.form
    identifier = data.get('identifier', '').strip() # email or phone
    password = data.get('password', '')

    if not (identifier and password):
        return jsonify({'success': False, 'message': 'Identifier and password required.'}), 400

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users 
        WHERE LOWER(email) = LOWER(?) OR phone = ?
    ''', (identifier, identifier))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid credentials for citizen user.'}), 401

    session['role'] = 'user'
    session['user_id'] = user['id']
    session['unique_id'] = user['unique_id']
    session['name'] = user['name']

    return jsonify({'success': True, 'redirect': '/user/dashboard'})

@app.route('/api/login/collector', methods=['POST'])
def login_collector():
    data = request.get_json(silent=True) or request.form
    identifier = data.get('identifier', '').strip() # email or phone
    password = data.get('password', '')

    if not (identifier and password):
        return jsonify({'success': False, 'message': 'Identifier and password required.'}), 400

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM collectors 
        WHERE LOWER(email) = LOWER(?) OR phone = ?
    ''', (identifier, identifier))
    col = cursor.fetchone()
    conn.close()

    if not col or not check_password_hash(col['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid credentials for waste collector.'}), 401

    session['role'] = 'collector'
    session['collector_id'] = col['id']
    session['unique_id'] = col['unique_id']
    session['name'] = col['name']
    session['area_assigned'] = col['area_assigned']

    return jsonify({'success': True, 'redirect': '/collector/dashboard'})

@app.route('/api/login/admin', methods=['POST'])
def login_admin():
    data = request.get_json(silent=True) or request.form
    identifier = data.get('identifier', '').strip() # email or phone
    password = data.get('password', '')

    if not (identifier and password):
        return jsonify({'success': False, 'message': 'Identifier and password required.'}), 400

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM admins 
        WHERE LOWER(email) = LOWER(?) OR phone = ?
    ''', (identifier, identifier))
    admin = cursor.fetchone()
    conn.close()

    if not admin or not check_password_hash(admin['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid admin credentials.'}), 401

    session['role'] = 'admin'
    session['admin_id'] = admin['id']
    session['name'] = admin['name']

    return jsonify({'success': True, 'redirect': '/admin/dashboard'})

@app.route('/api/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/me', methods=['GET'])
def get_current_user():
    role = session.get('role')
    if not role:
        return jsonify({'authenticated': False})

    conn = db.get_db()
    cursor = conn.cursor()

    if role == 'user':
        cursor.execute("SELECT id, unique_id, name, age, area, email, phone, gender FROM users WHERE id = ?", (session.get('user_id'),))
        u = cursor.fetchone()
        conn.close()
        if not u:
            return jsonify({'authenticated': False})
        return jsonify({'authenticated': True, 'role': 'user', 'data': dict(u)})

    elif role == 'collector':
        cursor.execute("SELECT id, unique_id, name, gender, phone, email, area_assigned, coins FROM collectors WHERE id = ?", (session.get('collector_id'),))
        c = cursor.fetchone()
        conn.close()
        if not c:
            return jsonify({'authenticated': False})
        return jsonify({'authenticated': True, 'role': 'collector', 'data': dict(c)})

    elif role == 'admin':
        cursor.execute("SELECT id, email, phone, name FROM admins WHERE id = ?", (session.get('admin_id'),))
        a = cursor.fetchone()
        conn.close()
        if not a:
            return jsonify({'authenticated': False})
        return jsonify({'authenticated': True, 'role': 'admin', 'data': dict(a)})

    conn.close()
    return jsonify({'authenticated': False})

# ----------------- USER PORTAL APIS ----------------- #

@app.route('/api/user/profile', methods=['GET', 'PUT'])
def user_profile():
    if session.get('role') != 'user':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, unique_id, name, age, area, email, phone, gender, created_at FROM users WHERE id = ?", (session.get('user_id'),))
        user = cursor.fetchone()
        conn.close()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        return jsonify({'success': True, 'user': dict(user)})

    elif request.method == 'PUT':
        data = request.get_json(silent=True) or request.form
        name = data.get('name', '').strip()
        age = data.get('age')
        area = data.get('area', '').strip()
        phone = data.get('phone', '').strip()
        gender = data.get('gender', '').strip()

        if not (name and area and phone):
            conn.close()
            return jsonify({'success': False, 'message': 'Name, Area, and Phone are required.'}), 400

        # Check phone conflict
        cursor.execute("SELECT id FROM users WHERE phone = ? AND id != ?", (phone, session.get('user_id')))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Phone number already taken by another user.'}), 400

        cursor.execute('''
            UPDATE users SET name = ?, age = ?, area = ?, phone = ?, gender = ?
            WHERE id = ?
        ''', (name, age, area, phone, gender, session.get('user_id')))
        conn.commit()
        conn.close()
        session['name'] = name
        return jsonify({'success': True, 'message': 'Profile updated successfully.'})

@app.route('/api/user/report', methods=['POST'])
def submit_complaint():
    if session.get('role') != 'user':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    description = request.form.get('description', '').strip()
    area = request.form.get('area', '').strip()

    if not description or not area:
        return jsonify({'success': False, 'message': 'Complaint description and area are required.'}), 400

    image_path = None
    if 'picture' in request.files:
        file = request.files['picture']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"user_cmp_{int(datetime.now().timestamp())}_{random.randint(100,999)}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"/static/uploads/{filename}"

    complaint_id = db.generate_complaint_id()
    now = datetime.now()
    deadline_at = (now + timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S")

    conn = db.get_db()
    cursor = conn.cursor()

    # Look up user details
    cursor.execute("SELECT unique_id, name FROM users WHERE id = ?", (session.get('user_id'),))
    user = cursor.fetchone()

    # Find assigned collector for this area (if any)
    cursor.execute("SELECT id, name FROM collectors WHERE LOWER(area_assigned) = LOWER(?) LIMIT 1", (area,))
    collector = cursor.fetchone()
    assigned_col_id = collector['id'] if collector else None
    assigned_col_name = collector['name'] if collector else 'Pending Assignment'

    status = 'In Progress' if assigned_col_id else 'Pending'

    cursor.execute('''
        INSERT INTO complaints (
            complaint_id, user_id, user_unique_id, user_name, area,
            description, image_path, status, assigned_collector_id,
            assigned_collector_name, deadline_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        complaint_id, session.get('user_id'), user['unique_id'], user['name'], area,
        description, image_path, status, assigned_col_id,
        assigned_col_name, deadline_at, now.strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Complaint {complaint_id} submitted successfully! 48-hour resolution timer started.',
        'complaint_id': complaint_id
    })

@app.route('/api/user/complaints', methods=['GET'])
def get_user_complaints():
    if session.get('role') != 'user':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM complaints 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session.get('user_id'),))
    rows = cursor.fetchall()
    conn.close()

    complaints = []
    now = datetime.now()

    for r in rows:
        c = dict(r)
        # Calculate SLA countdown
        try:
            deadline = datetime.strptime(c['deadline_at'], "%Y-%m-%d %H:%M:%S")
            diff = deadline - now
            if diff.total_seconds() > 0:
                hours = int(diff.total_seconds() // 3600)
                minutes = int((diff.total_seconds() % 3600) // 60)
                c['sla_time_left'] = f"{hours}h {minutes}m remaining"
                c['sla_percentage'] = max(0, min(100, int((48 - (diff.total_seconds() / 3600)) / 48 * 100)))
                c['is_overdue'] = False
            else:
                c['sla_time_left'] = "Overdue (Passed 48h limit)"
                c['sla_percentage'] = 100
                c['is_overdue'] = True
        except Exception:
            c['sla_time_left'] = "48h window"
            c['sla_percentage'] = 50
            c['is_overdue'] = False

        complaints.append(c)

    return jsonify({'success': True, 'complaints': complaints})

@app.route('/api/user/rewards', methods=['GET'])
def get_user_rewards():
    if session.get('role') != 'user':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE user_id = ?", (session.get('user_id'),))
    total_complaints = cursor.fetchone()[0]
    conn.close()

    # Reward criteria:
    # 25 = Bronze
    # 50 = Silver
    # 100 = Gold
    badges = [
        {
            'name': 'Bronze Eco-Sentinel',
            'required': 25,
            'color': 'amber',
            'icon': '🥉',
            'unlocked': total_complaints >= 25,
            'description': 'Awarded for filing 25 community waste reports'
        },
        {
            'name': 'Silver Green Guardian',
            'required': 50,
            'color': 'slate',
            'icon': '🥈',
            'unlocked': total_complaints >= 50,
            'description': 'Awarded for filing 50 community waste reports'
        },
        {
            'name': 'Gold Planet Champion',
            'required': 100,
            'color': 'yellow',
            'icon': '🥇',
            'unlocked': total_complaints >= 100,
            'description': 'Awarded for filing 100 community waste reports'
        }
    ]

    # Current level & next target
    if total_complaints < 25:
        current_badge = "Citizen Cadet"
        next_target = 25
        progress_pct = int((total_complaints / 25) * 100)
    elif total_complaints < 50:
        current_badge = "Bronze Eco-Sentinel"
        next_target = 50
        progress_pct = int(((total_complaints - 25) / 25) * 100)
    elif total_complaints < 100:
        current_badge = "Silver Green Guardian"
        next_target = 100
        progress_pct = int(((total_complaints - 50) / 50) * 100)
    else:
        current_badge = "Gold Planet Champion"
        next_target = 100
        progress_pct = 100

    return jsonify({
        'success': True,
        'total_complaints': total_complaints,
        'current_badge': current_badge,
        'next_target': next_target,
        'progress_pct': min(100, progress_pct),
        'badges': badges
    })

@app.route('/api/user/notifications', methods=['GET'])
def get_user_notifications():
    if session.get('role') != 'user':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session.get('user_id'),))
    notifications = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (session.get('user_id'),))
    unread_count = cursor.fetchone()[0]
    conn.close()

    return jsonify({'success': True, 'notifications': notifications, 'unread_count': unread_count})

@app.route('/api/user/notifications/mark-read', methods=['POST'])
def mark_user_notifications_read():
    if session.get('role') != 'user':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (session.get('user_id'),))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/user/area-details', methods=['GET'])
def get_area_details():
    area_name = request.args.get('area')
    if not area_name and session.get('role') == 'user':
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT area FROM users WHERE id = ?", (session.get('user_id'),))
        u = cursor.fetchone()
        conn.close()
        if u:
            area_name = u['area']

    if not area_name:
        area_name = "Downtown Sector 1"

    conn = db.get_db()
    cursor = conn.cursor()

    # Get Dumping Spots for this area
    cursor.execute("SELECT * FROM area_dumping_spots WHERE LOWER(area_name) = LOWER(?)", (area_name,))
    spots = [dict(r) for r in cursor.fetchall()]

    # If no exact spots, fetch general spots
    if not spots:
        cursor.execute("SELECT * FROM area_dumping_spots LIMIT 3")
        spots = [dict(r) for r in cursor.fetchall()]

    # Get Collectors assigned to this area
    cursor.execute('''
        SELECT unique_id, name, gender, phone, email, area_assigned 
        FROM collectors 
        WHERE LOWER(area_assigned) = LOWER(?)
    ''', (area_name,))
    collectors = [dict(r) for r in cursor.fetchall()]

    # Get active complaints in this area
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE LOWER(area) = LOWER(?) AND status != 'Completed'", (area_name,))
    active_complaints_count = cursor.fetchone()[0]

    # All distinct areas for switcher
    cursor.execute("SELECT DISTINCT area_name FROM area_dumping_spots")
    all_areas = [r['area_name'] for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'current_area': area_name,
        'active_complaints_count': active_complaints_count,
        'dumping_spots': spots,
        'collectors': collectors,
        'available_areas': all_areas
    })

# ----------------- WASTE COLLECTOR PORTAL APIS ----------------- #

@app.route('/api/collector/dashboard', methods=['GET'])
def get_collector_dashboard():
    if session.get('role') != 'collector':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    collector_id = session.get('collector_id')
    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM collectors WHERE id = ?", (collector_id,))
    col = cursor.fetchone()
    if not col:
        conn.close()
        return jsonify({'success': False, 'message': 'Collector not found'}), 404

    area = col['area_assigned']

    # Complains in this area
    cursor.execute("SELECT * FROM complaints WHERE LOWER(area) = LOWER(?) ORDER BY created_at DESC", (area,))
    all_complaints = [dict(r) for r in cursor.fetchall()]

    pending = [c for c in all_complaints if c['status'] in ('Pending', 'In Progress')]
    resolved = [c for c in all_complaints if c['status'] == 'Completed']

    # Daily progress calculation:
    # Target: complete pending tasks assigned to area
    total_tasks = len(all_complaints)
    resolved_count = len(resolved)
    progress_percentage = int((resolved_count / total_tasks * 100)) if total_tasks > 0 else 100

    conn.close()

    return jsonify({
        'success': True,
        'collector': dict(col),
        'stats': {
            'total_assigned': total_tasks,
            'pending_count': len(pending),
            'resolved_count': resolved_count,
            'progress_percentage': progress_percentage
        },
        'pending_complaints': pending,
        'resolved_complaints': resolved
    })

@app.route('/api/collector/resolve-complaint', methods=['POST'])
def resolve_complaint():
    if session.get('role') != 'collector':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    complaint_id = request.form.get('complaint_id')
    notes = request.form.get('notes', 'Area thoroughly sanitized and waste disposed.')

    if not complaint_id:
        return jsonify({'success': False, 'message': 'Complaint ID is required.'}), 400

    if 'resolved_picture' not in request.files:
        return jsonify({'success': False, 'message': 'Picture submission is mandatory to verify place resolution.'}), 400

    file = request.files['resolved_picture']
    if not (file and file.filename and allowed_file(file.filename)):
        return jsonify({'success': False, 'message': 'A valid picture file is required for verification.'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"col_res_{int(datetime.now().timestamp())}_{random.randint(100,999)}.{ext}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    resolved_image_path = f"/static/uploads/{filename}"

    collector_id = session.get('collector_id')
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")

    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM collectors WHERE id = ?", (collector_id,))
    col = cursor.fetchone()

    cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
    cmp = cursor.fetchone()
    if not cmp:
        conn.close()
        return jsonify({'success': False, 'message': 'Complaint not found.'}), 404

    # Update complaint
    cursor.execute('''
        UPDATE complaints SET 
            status = 'Completed',
            assigned_collector_id = ?,
            assigned_collector_name = ?,
            resolved_image_path = ?,
            resolved_notes = ?,
            resolved_at = ?,
            user_notified = 1
        WHERE complaint_id = ?
    ''', (col['id'], col['name'], resolved_image_path, notes, now_str, complaint_id))

    # Send Notification to Citizen User: "task completed"
    cursor.execute('''
        INSERT INTO notifications (user_id, title, message, complaint_id, is_read)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        cmp['user_id'],
        'Task Completed! 🌟',
        f'Your complaint {complaint_id} in {cmp["area"]} has been cleared and verified by Waste Collector {col["name"]}.',
        complaint_id,
        0
    ))

    # Check collector daily progress for digital coins increment:
    # "Reward section that increment by one on the daily basis after completing the 70% progress bar daily"
    cursor.execute('''
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as resolved
        FROM complaints 
        WHERE LOWER(area) = LOWER(?)
    ''', (col['area_assigned'],))
    stats = cursor.fetchone()
    total_area_tasks = stats['total'] or 1
    resolved_area_tasks = stats['resolved'] or 1
    progress_bar = int((resolved_area_tasks / total_area_tasks) * 100)

    coin_rewarded = False
    new_coins = col['coins']

    # Check if collector reached 70% and hasn't received today's daily coin yet
    if progress_bar >= 70:
        if col['daily_progress_date'] != today_str:
            new_coins += 1
            coin_rewarded = True
            cursor.execute('''
                UPDATE collectors 
                SET coins = ?, daily_progress_date = ?, daily_resolved_today = daily_resolved_today + 1
                WHERE id = ?
            ''', (new_coins, today_str, collector_id))
        else:
            cursor.execute('''
                UPDATE collectors 
                SET daily_resolved_today = daily_resolved_today + 1
                WHERE id = ?
            ''', (collector_id,))
    else:
        cursor.execute('''
            UPDATE collectors 
            SET daily_resolved_today = daily_resolved_today + 1
            WHERE id = ?
        ''', (collector_id,))

    conn.commit()
    conn.close()

    msg = f'Task {complaint_id} marked Completed! Verified picture uploaded.'
    if coin_rewarded:
        msg += ' 🪙 Milestone Reached: Progress bar reached 70%+! 1 Digital Coin added to your daily wallet.'

    return jsonify({
        'success': True,
        'message': msg,
        'coin_rewarded': coin_rewarded,
        'new_coins': new_coins,
        'progress_bar': progress_bar
    })

@app.route('/api/collector/profile', methods=['GET'])
def get_collector_profile():
    if session.get('role') != 'collector':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM collectors WHERE id = ?", (session.get('collector_id'),))
    col = cursor.fetchone()
    conn.close()

    if not col:
        return jsonify({'success': False, 'message': 'Collector not found'}), 404

    # End of month cash conversion logic (1 Digital Coin = ₹100 / $15)
    coin_rate_inr = 100
    coin_rate_usd = 15
    cash_value_inr = col['coins'] * coin_rate_inr
    cash_value_usd = col['coins'] * coin_rate_usd

    return jsonify({
        'success': True,
        'collector': dict(col),
        'reward_details': {
            'coins': col['coins'],
            'cash_value_inr': cash_value_inr,
            'cash_value_usd': cash_value_usd,
            'daily_awarded_today': (col['daily_progress_date'] == datetime.now().strftime("%Y-%m-%d")),
            'conversion_rate_text': '1 Digital Coin = ₹100 INR / $15 USD (Converted and disbursed at month end)'
        }
    })

# ----------------- ADMIN PORTAL APIS (Single User) ----------------- #

@app.route('/api/admin/dashboard', methods=['GET'])
def get_admin_dashboard():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM collectors")
    total_collectors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Completed'")
    total_resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
    total_pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    total_in_progress = cursor.fetchone()[0]

    # Recent complaints
    cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC LIMIT 5")
    recent = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'counts': {
            'total_users': total_users,
            'total_complaints': total_complaints,
            'total_collectors': total_collectors,
            'total_resolved': total_resolved,
            'total_pending': total_pending,
            'total_in_progress': total_in_progress
        },
        'recent_complaints': recent
    })

@app.route('/api/admin/waste-area-alert', methods=['GET'])
def get_waste_area_alert():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()

    # Get all distinct areas
    cursor.execute('''
        SELECT DISTINCT area FROM complaints
        UNION
        SELECT DISTINCT area_name FROM area_dumping_spots
        UNION
        SELECT DISTINCT area_assigned FROM collectors
    ''')
    areas = [r[0] for r in cursor.fetchall() if r[0]]

    area_stats = []
    for area in areas:
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status != 'Completed' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as resolved_count
            FROM complaints
            WHERE LOWER(area) = LOWER(?)
        ''', (area,))
        row = cursor.fetchone()
        active = row['active_count'] or 0
        resolved = row['resolved_count'] or 0
        total = row['total'] or 0

        # Assigned collector
        cursor.execute("SELECT name, phone FROM collectors WHERE LOWER(area_assigned) = LOWER(?) LIMIT 1", (area,))
        col = cursor.fetchone()
        col_name = col['name'] if col else 'Unassigned'
        col_phone = col['phone'] if col else 'N/A'

        # Fetch recent complaint titles/descriptions for this area
        cursor.execute("SELECT complaint_id, description, status, created_at FROM complaints WHERE LOWER(area) = LOWER(?) ORDER BY created_at DESC LIMIT 5", (area,))
        complaint_list = [dict(c) for c in cursor.fetchall()]

        # Classification based on user requirement:
        # 4 categories based on color:
        # High: Red
        # Medium: Orange
        # Low: Yellow
        # Clear: Green
        if active > 5:
            category = 'High'
            color = 'red'
            badge_class = 'bg-red-500 text-white'
        elif active >= 3:
            category = 'Medium'
            color = 'orange'
            badge_class = 'bg-orange-500 text-white'
        elif active >= 1:
            category = 'Low'
            color = 'yellow'
            badge_class = 'bg-yellow-400 text-gray-900'
        else:
            category = 'Clear'
            color = 'green'
            badge_class = 'bg-emerald-500 text-white'

        area_stats.append({
            'area_name': area,
            'active_count': active,
            'resolved_count': resolved,
            'total_count': total,
            'category': category,
            'color': color,
            'badge_class': badge_class,
            'collector_name': col_name,
            'collector_phone': col_phone,
            'complaints': complaint_list
        })

    conn.close()

    # Sort so highest active complaints come first
    area_stats.sort(key=lambda x: x['active_count'], reverse=True)

    # Group by category for quick lookup
    grouped = {
        'High': [a for a in area_stats if a['category'] == 'High'],
        'Medium': [a for a in area_stats if a['category'] == 'Medium'],
        'Low': [a for a in area_stats if a['category'] == 'Low'],
        'Clear': [a for a in area_stats if a['category'] == 'Clear'],
    }

    return jsonify({
        'success': True,
        'all_areas': area_stats,
        'grouped': grouped,
        'summary': {
            'high_count': len(grouped['High']),
            'medium_count': len(grouped['Medium']),
            'low_count': len(grouped['Low']),
            'clear_count': len(grouped['Clear']),
        }
    })

@app.route('/api/admin/loggers', methods=['GET'])
def get_admin_loggers():
    """Users ID and details in form of table"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            u.id, u.unique_id, u.name, u.age, u.area, u.email, u.phone, u.gender, u.created_at,
            COUNT(c.id) as total_reports,
            SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) as resolved_reports
        FROM users u
        LEFT JOIN complaints c ON u.id = c.user_id
        GROUP BY u.id
        ORDER BY u.id ASC
    ''')
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'success': True, 'users': users})

@app.route('/api/admin/employees', methods=['GET', 'POST'])
def handle_admin_employees():
    """Collector details in form of table, plus employee registration"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = db.get_db()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('''
            SELECT 
                c.id, c.unique_id, c.name, c.gender, c.phone, c.email, c.area_assigned, c.coins, c.created_at,
                COUNT(cmp.id) as total_assigned,
                SUM(CASE WHEN cmp.status = 'Completed' THEN 1 ELSE 0 END) as total_resolved
            FROM collectors c
            LEFT JOIN complaints cmp ON c.id = cmp.assigned_collector_id
            GROUP BY c.id
            ORDER BY c.id ASC
        ''')
        collectors = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return jsonify({'success': True, 'collectors': collectors})

    elif request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        name = data.get('name', '').strip()
        gender = data.get('gender', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip().lower()
        area_assigned = data.get('area_assigned', '').strip()
        password = data.get('password', 'col123')

        if not (name and phone and email and area_assigned):
            conn.close()
            return jsonify({'success': False, 'message': 'Please fill all required collector details.'}), 400

        # Check existing
        cursor.execute("SELECT id FROM collectors WHERE email = ? OR phone = ?", (email, phone))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Collector email or phone already registered.'}), 400

        unique_id = db.generate_collector_id()
        pwd_hash = generate_password_hash(password)

        cursor.execute('''
            INSERT INTO collectors (unique_id, name, gender, phone, email, area_assigned, password_hash, coins)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        ''', (unique_id, name, gender, phone, email, area_assigned, pwd_hash))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'New Collector registered with ID {unique_id}.',
            'unique_id': unique_id
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
