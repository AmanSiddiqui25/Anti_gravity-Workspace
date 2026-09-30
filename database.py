import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random

DB_PATH = os.path.join(os.path.dirname(__file__), 'ecoclean.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER,
        area TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        gender TEXT,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Collectors Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS collectors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        gender TEXT,
        phone TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        area_assigned TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        coins INTEGER DEFAULT 0,
        daily_progress_date TEXT,
        daily_resolved_today INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Admin Table (Single user login system)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Complaints Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        user_unique_id TEXT NOT NULL,
        user_name TEXT NOT NULL,
        area TEXT NOT NULL,
        description TEXT NOT NULL,
        image_path TEXT,
        status TEXT DEFAULT 'Pending', -- 'Pending', 'In Progress', 'Completed'
        assigned_collector_id INTEGER,
        assigned_collector_name TEXT,
        resolved_image_path TEXT,
        resolved_notes TEXT,
        deadline_at TIMESTAMP NOT NULL,
        resolved_at TIMESTAMP,
        user_notified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (assigned_collector_id) REFERENCES collectors(id)
    )
    ''')

    # Area Dumping Spots Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS area_dumping_spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_name TEXT NOT NULL,
        spot_name TEXT NOT NULL,
        location_landmark TEXT,
        severity TEXT DEFAULT 'Medium', -- 'Low', 'Medium', 'High', 'Critical'
        notes TEXT,
        last_inspected TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Notifications Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        complaint_id TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

def seed_data_if_empty():
    conn = get_db()
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        # Pre-seed Admin
        admin_pass = generate_password_hash("admin123")
        cursor.execute('''
            INSERT INTO admins (email, phone, name, password_hash)
            VALUES (?, ?, ?, ?)
        ''', ('admin@ecoclean.org', '9876543210', 'System Administrator', admin_pass))

    # Pre-seed Dumping Spots for standard areas
    cursor.execute("SELECT COUNT(*) FROM area_dumping_spots")
    if cursor.fetchone()[0] == 0:
        spots = [
            ("Downtown Sector 1", "Market Dump Yard #4", "Behind Central Supermarket", "High", "Heavy commercial organic & plastic waste"),
            ("Downtown Sector 1", "Subway North Transit Bin", "Opposite Gate 2", "Medium", "Daily commuter trash and cartons"),
            ("Greenwood Park", "East Lake Promenade Bin", "Next to Botanical Garden Gate", "Low", "Litter and fallen garden leaves"),
            ("Riverside Colony", "Old Pier Waste Hub", "Near Riverbank Steps", "High", "Unregulated household dumping site"),
            ("Riverside Colony", "Lane 7 Community Dump", "Corner of Rose Street", "Medium", "Overflowing local dumpster"),
            ("Metro Central", "Platform 3 Backlot", "Metro Station West Side", "Critical", "Heavy public refuse and construction debris"),
            ("Sunnyvale West", "School Lane Collection Spot", "Beside Govt High School", "Low", "Dry leaves and paper waste"),
            ("Industrial Zone B", "Plot 44 Chemical Waste Lot", "Sector B Boulevard", "Critical", "Industrial non-hazardous scrap and drums"),
            ("Industrial Zone B", "Truck Terminal Dump", "Gate 5 Depot", "High", "Tire scraps and packaging material"),
            ("Old Town Square", "Heritage Market Bin", "Behind Clock Tower", "Medium", "Food street vegetable peelings and cups"),
            ("Highland Heights", "Valley View Corner Spot", "Near Ridge Water Tank", "Low", "Light residential packaging")
        ]
        cursor.executemany('''
            INSERT INTO area_dumping_spots (area_name, spot_name, location_landmark, severity, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', spots)

    # Pre-seed Collectors
    cursor.execute("SELECT COUNT(*) FROM collectors")
    if cursor.fetchone()[0] == 0:
        collectors_data = [
            ("COL-2001", "Rajesh Kumar", "Male", "9811002233", "rajesh.col@ecoclean.org", "Downtown Sector 1", generate_password_hash("col123"), 14),
            ("COL-2002", "Sunita Devi", "Female", "9822113344", "sunita.col@ecoclean.org", "Greenwood Park", generate_password_hash("col123"), 22),
            ("COL-2003", "Amit Sharma", "Male", "9833224455", "amit.col@ecoclean.org", "Riverside Colony", generate_password_hash("col123"), 9),
            ("COL-2004", "Farhan Akhtar", "Male", "9844335566", "farhan.col@ecoclean.org", "Metro Central", generate_password_hash("col123"), 18),
            ("COL-2005", "Priya Verma", "Female", "9855446677", "priya.col@ecoclean.org", "Industrial Zone B", generate_password_hash("col123"), 5),
            ("COL-2006", "Vikram Rathore", "Male", "9866557788", "vikram.col@ecoclean.org", "Sunnyvale West", generate_password_hash("col123"), 30),
            ("COL-2007", "Kavita Rao", "Female", "9877668899", "kavita.col@ecoclean.org", "Old Town Square", generate_password_hash("col123"), 12)
        ]
        cursor.executemany('''
            INSERT INTO collectors (unique_id, name, gender, phone, email, area_assigned, password_hash, coins)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', collectors_data)

    # Pre-seed Users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users_data = [
            ("USR-1001", "Aarav Patel", 29, "Downtown Sector 1", "aarav@gmail.com", "9123456780", "Male", generate_password_hash("user123")),
            ("USR-1002", "Neha Sengupta", 34, "Riverside Colony", "neha@gmail.com", "9123456781", "Female", generate_password_hash("user123")),
            ("USR-1003", "Rohan Mehta", 42, "Metro Central", "rohan@gmail.com", "9123456782", "Male", generate_password_hash("user123")),
            ("USR-1004", "Ananya Iyer", 26, "Greenwood Park", "ananya@gmail.com", "9123456783", "Female", generate_password_hash("user123")),
            ("USR-1005", "Kabir Das", 31, "Industrial Zone B", "kabir@gmail.com", "9123456784", "Male", generate_password_hash("user123")),
            ("USR-1006", "Pooja Malhotra", 28, "Downtown Sector 1", "pooja@gmail.com", "9123456785", "Female", generate_password_hash("user123"))
        ]
        cursor.executemany('''
            INSERT INTO users (unique_id, name, age, area, email, phone, gender, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', users_data)

    # Pre-seed Sample Complaints across different areas to demonstrate Red/Orange/Yellow/Green categories
    cursor.execute("SELECT COUNT(*) FROM complaints")
    if cursor.fetchone()[0] == 0:
        now = datetime.now()
        complaints_data = [
            # Downtown Sector 1 (High Alert - 6 complaints)
            ("CMP-5001", 1, "USR-1001", "Aarav Patel", "Downtown Sector 1", "Overflowing plastic dump near sector 1 bus stop.", "/static/images/waste_sample1.jpg", "Pending", 1, "Rajesh Kumar", (now + timedelta(hours=36)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5002", 1, "USR-1001", "Aarav Patel", "Downtown Sector 1", "Foul smelling garbage piled near market gate.", "/static/images/waste_sample2.jpg", "Pending", 1, "Rajesh Kumar", (now + timedelta(hours=28)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5003", 6, "USR-1006", "Pooja Malhotra", "Downtown Sector 1", "Construction dust and broken bricks blocking drainage.", None, "In Progress", 1, "Rajesh Kumar", (now + timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5004", 6, "USR-1006", "Pooja Malhotra", "Downtown Sector 1", "Discarded cartons and packing polystyrene scattered on footpath.", None, "Pending", 1, "Rajesh Kumar", (now + timedelta(hours=42)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5005", 1, "USR-1001", "Aarav Patel", "Downtown Sector 1", "Heavy glass bottles dumped dangerously near park bench.", None, "Pending", 1, "Rajesh Kumar", (now + timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5006", 1, "USR-1001", "Aarav Patel", "Downtown Sector 1", "Rotting vegetables left behind by weekly bazaar vendors.", None, "Pending", 1, "Rajesh Kumar", (now + timedelta(hours=20)).strftime("%Y-%m-%d %H:%M:%S")),

            # Metro Central (High Alert - 6 complaints)
            ("CMP-5007", 3, "USR-1003", "Rohan Mehta", "Metro Central", "Major refuse accumulation outside platform 2.", None, "Pending", 4, "Farhan Akhtar", (now + timedelta(hours=44)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5008", 3, "USR-1003", "Rohan Mehta", "Metro Central", "Single use plastic cups clogging stormwater drain.", None, "Pending", 4, "Farhan Akhtar", (now + timedelta(hours=18)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5009", 3, "USR-1003", "Rohan Mehta", "Metro Central", "Food wrapper piles attracting stray animals near ticket counter.", None, "In Progress", 4, "Farhan Akhtar", (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5010", 3, "USR-1003", "Rohan Mehta", "Metro Central", "Stagnant waste water mixed with wet garbage in subway tunnel entrance.", None, "Pending", 4, "Farhan Akhtar", (now + timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5011", 3, "USR-1003", "Rohan Mehta", "Metro Central", "Unattended broken bins spilling onto the main road.", None, "Pending", 4, "Farhan Akhtar", (now + timedelta(hours=35)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5012", 3, "USR-1003", "Rohan Mehta", "Metro Central", "Bio-waste dumped outside clinic.", None, "Pending", 4, "Farhan Akhtar", (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")),

            # Riverside Colony (Medium Alert - 4 complaints)
            ("CMP-5013", 2, "USR-1002", "Neha Sengupta", "Riverside Colony", "Plastic bottles floating along riverside walkway.", None, "Pending", 3, "Amit Sharma", (now + timedelta(hours=29)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5014", 2, "USR-1002", "Neha Sengupta", "Riverside Colony", "Lane 7 bin turned upside down, rubbish strewn across path.", None, "In Progress", 3, "Amit Sharma", (now + timedelta(hours=19)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5015", 2, "USR-1002", "Neha Sengupta", "Riverside Colony", "Decaying tree branches and garden refuse blocking walkway.", None, "Pending", 3, "Amit Sharma", (now + timedelta(hours=40)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5016", 2, "USR-1002", "Neha Sengupta", "Riverside Colony", "Household trash bags piled around electric transformer.", None, "Pending", 3, "Amit Sharma", (now + timedelta(hours=15)).strftime("%Y-%m-%d %H:%M:%S")),

            # Industrial Zone B (Medium Alert - 3 complaints)
            ("CMP-5017", 5, "USR-1005", "Kabir Das", "Industrial Zone B", "Scrap metal and rubber shavings spilled on road shoulder.", None, "Pending", 5, "Priya Verma", (now + timedelta(hours=38)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5018", 5, "USR-1005", "Kabir Das", "Industrial Zone B", "Greasy sludge barrels left unattended near canal.", None, "Pending", 5, "Priya Verma", (now + timedelta(hours=22)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5019", 5, "USR-1005", "Kabir Das", "Industrial Zone B", "Packaging straps caught on roadside fences.", None, "In Progress", 5, "Priya Verma", (now + timedelta(hours=11)).strftime("%Y-%m-%d %H:%M:%S")),

            # Old Town Square (Low Alert - 2 complaints)
            ("CMP-5020", 4, "USR-1004", "Ananya Iyer", "Old Town Square", "Fly-tipping behind heritage statue pedestal.", None, "Pending", 7, "Kavita Rao", (now + timedelta(hours=45)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5021", 4, "USR-1004", "Ananya Iyer", "Old Town Square", "Torn posters and cardboard cartons near alley.", None, "Pending", 7, "Kavita Rao", (now + timedelta(hours=27)).strftime("%Y-%m-%d %H:%M:%S")),

            # Greenwood Park (Low Alert - 1 complaint)
            ("CMP-5022", 4, "USR-1004", "Ananya Iyer", "Greenwood Park", "Empty snack packets and beverage cans near playground.", None, "Pending", 2, "Sunita Devi", (now + timedelta(hours=32)).strftime("%Y-%m-%d %H:%M:%S")),

            # Completed complaints for demo tracking & history
            ("CMP-5023", 1, "USR-1001", "Aarav Patel", "Downtown Sector 1", "Dumpster overflowing near primary school.", "/static/images/waste_sample1.jpg", "Completed", 1, "Rajesh Kumar", (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S")),
            ("CMP-5024", 2, "USR-1002", "Neha Sengupta", "Riverside Colony", "Plastic bags discarded by fishermen near boat jetty.", None, "Completed", 3, "Amit Sharma", (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"))
        ]

        for cmp_data in complaints_data:
            cursor.execute('''
                INSERT INTO complaints (
                    complaint_id, user_id, user_unique_id, user_name, area, 
                    description, image_path, status, assigned_collector_id, 
                    assigned_collector_name, deadline_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', cmp_data)

        # Mark completed ones with resolved details
        cursor.execute('''
            UPDATE complaints SET 
                resolved_image_path = '/static/images/resolved_sample.jpg',
                resolved_notes = 'Area thoroughly swept, disinfected, and bins replaced with fresh covers.',
                resolved_at = CURRENT_TIMESTAMP,
                user_notified = 1
            WHERE status = 'Completed'
        ''')

        # Insert notification for Aarav Patel and Neha Sengupta
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, complaint_id, is_read)
            VALUES 
            (1, 'Task Completed! 🌟', 'Collector Rajesh Kumar has cleared your complaint CMP-5023 in Downtown Sector 1. Photo proof verified.', 'CMP-5023', 0),
            (2, 'Task Completed! 🌟', 'Collector Amit Sharma has cleared your complaint CMP-5024 in Riverside Colony. Thank you for making our city clean!', 'CMP-5024', 0)
        ''')

        # Let's seed additional complaints for Aarav Patel (USR-1001) so he is at 26 complaints to display the Bronze Badge!
        # Aarav already has CMP-5001, 5002, 5005, 5006, 5023 (5 complaints). Let's insert 21 completed past complaints for Aarav
        # so his total count is 26, unlocking the Bronze Badge (25 = bronze)!
        for i in range(1, 22):
            cid = f"CMP-40{i:02d}"
            cursor.execute('''
                INSERT INTO complaints (
                    complaint_id, user_id, user_unique_id, user_name, area,
                    description, image_path, status, assigned_collector_id,
                    assigned_collector_name, deadline_at, resolved_at, user_notified, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cid, 1, "USR-1001", "Aarav Patel", "Downtown Sector 1",
                f"Historical reported waste item #{i} successfully cleared.",
                None, "Completed", 1, "Rajesh Kumar",
                (now - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
                (now - timedelta(days=i, hours=-4)).strftime("%Y-%m-%d %H:%M:%S"),
                1,
                (now - timedelta(days=i, hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            ))

    conn.commit()
    conn.close()

# Helper ID Generators
def generate_user_id():
    conn = get_db()
    cursor = conn.cursor()
    while True:
        num = random.randint(1000, 9999)
        uid = f"USR-{num}"
        cursor.execute("SELECT id FROM users WHERE unique_id = ?", (uid,))
        if not cursor.fetchone():
            conn.close()
            return uid

def generate_collector_id():
    conn = get_db()
    cursor = conn.cursor()
    while True:
        num = random.randint(1000, 9999)
        cid = f"COL-{num}"
        cursor.execute("SELECT id FROM collectors WHERE unique_id = ?", (cid,))
        if not cursor.fetchone():
            conn.close()
            return cid

def generate_complaint_id():
    conn = get_db()
    cursor = conn.cursor()
    while True:
        num = random.randint(10000, 99999)
        cid = f"CMP-{num}"
        cursor.execute("SELECT id FROM complaints WHERE complaint_id = ?", (cid,))
        if not cursor.fetchone():
            conn.close()
            return cid
