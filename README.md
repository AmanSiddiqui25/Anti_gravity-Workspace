# 🌿 EcoClean - Smart Municipal Waste Tracking & Resolution Platform

A complete full-stack web application designed for municipal waste monitoring, featuring three dedicated roles: **Citizen Users**, **Waste Collectors**, and a **Municipal Administrator** (single user system).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested with Python 3.14)

### 1. Installation
Clone or open the project folder in your terminal:
```bash
# Activate virtual environment
.\.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate (Linux/macOS)

# Dependencies are pre-installed, or run:
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://localhost:5000`**

### 3. Run Automated Tests
```bash
python test_system.py
```

---

## 🔑 Demo Access Credentials

The database comes pre-seeded with real sample complaints, active areas, collectors, and citizen accounts. You can also use the one-click **"⚡ Autofill Demo"** buttons on the login page:

| Role | Email / Phone | Password | Details |
| :--- | :--- | :--- | :--- |
| **Municipal Admin** | `admin@ecoclean.org` or `9876543210` | `admin123` | Single-user central control center |
| **Waste Collector** | `rajesh.col@ecoclean.org` or `9811002233` | `col123` | Assigned to *Downtown Sector 1* |
| **Citizen User** | `aarav@gmail.com` or `9123456780` | `user123` | Resident in *Downtown Sector 1* (26+ complaints filed, Bronze unlocked) |

---

## 🌟 Key Components & Feature Specifications

### 1. 👤 Citizen User Module
- **Dual Identifier Login**: Sign in using **Email ID or Phone Number** + Password.
- **Registration**: Captures *Full Name, Age, Gender, Locality / Area, Email ID, Phone Number*. Automatically generates a **Unique Citizen ID (e.g. `USR-1001`)**.
- **Homepage Options**:
  1. **Report Box**:
     - Complaint details description.
     - Area selection.
     - **Picture Submission Option** (drag-and-drop file upload with live image preview).
  2. **Score / Reward**:
     - Progressively tracks total complaints filed by the citizen.
     - Badges awarded:
       - **25 Complaints**: 🥉 Bronze Eco-Sentinel
       - **50 Complaints**: 🥈 Silver Green Guardian
       - **100 Complaints**: 🥇 Gold Planet Champion
     - Visual milestone progress bar & unlocked badge glow.
  3. **Profile**:
     - Full citizen details card with **Edit Profile** modal (updates name, age, area, phone, gender).
     - **Complaint History**: Comprehensive audit log of all filed complaints with status badges and timestamps.
  4. **Tracking / Completed**:
     - **48-Hour SLA Countdown Timer**: Real-time ticker counting down hours and minutes remaining within the 48-hour municipal window.
     - **3-Stage Visual Pipeline**: *Reported → Collector Dispatched → Task Completed*.
     - **Before & After Photos**: Shows citizen's initial waste photo alongside collector's verified clean-up photo.
     - **Task Completed Notification Alert**: Instant notification banner and bell icon badge alerting the user when the collector marks the task resolved.
  5. **Area Details**:
     - **Dumping Spots**: Lists designated community dumping hotspots in the user's area with severity ratings (*Critical, High, Medium, Low*) and landmarks.
     - **Assigned Collectors**: Contact directory displaying names, IDs, and phone numbers of municipal collectors assigned to their area.

---

### 2. 🚛 Waste Collector Module
- **Dual Identifier Login**: Sign in via Email ID or Phone Number + Password.
- **Collector Details**: Unique Collector ID (e.g. `COL-2001`), Name, Gender, Phone, Email, Assigned Municipal Area.
- **Homepage Options**:
  1. **Dashboard**:
     - Statistical breakdown: *Pending Complaints, Completed / Resolved Complaints, Total Assigned Area Tasks*.
     - Quick-action pending task queue and resolved history.
  2. **Personal Progress**:
     - Lists all complaints in the collector's assigned area with citizen contact info, location, issue description, and photo.
     - **Verification Resolution Action**: Collector must upload a **mandatory photo of the cleaned place** and enter sanitary notes to resolve the complaint.
     - **Interactive Progress Bar**: Dynamically calculates completion rate (`Resolved / Total * 100%`) and animates upwards as tasks are cleared.
  3. **Profile & Rewards**:
     - Collector credentials and service record.
     - **Daily Milestone Reward**: Daily progress bar increments the collector's wallet by **+1 Digital Coin 🪙** upon completing **70% or more** of their assigned area's tasks for the day.
     - **Month-End Cash Conversion**: Digital Coins accumulate and can be converted into cash at **1 Coin = ₹100 INR / $15 USD** with simulated disbursement statements.

---

### 3. 🛡️ Municipal Admin Module (Single User System)
- **Dedicated Single-User Login**: Secured access via Email or Phone Number.
- **Homepage Options**:
  1. **Dashboard**:
     - Real-time KPI counter cards:
       - **Total Users**
       - **Total Complains**
       - **Total Collectors**
       - **Total Resolved Complains**
     - Live recent complaints activity stream and quick navigation links.
  2. **Waste Area Alert**:
     - Dynamically categorizes all municipal sectors into **4 color alert levels** based on active user complaints:
       - 🔴 **High Alert (Red)**: `> 5` active complaints
       - 🟠 **Medium Alert (Orange)**: `3 - 5` active complaints
       - 🟡 **Low Alert (Yellow)**: `1 - 2` active complaints
       - 🟢 **Clear Areas (Green)**: `0` active complaints (100% clean)
     - **Interactable Color Buttons**: Clicking any color button dynamically filters and renders the areas falling under that alert tier, detailing active issues, assigned collectors, and individual user complaints.
  3. **Loggers (Users Directory)**:
     - Tabular registry displaying: *User ID (`USR-XXXX`), Name, Age, Gender, Area, Email ID, Phone Number, Reports Filed, and Joined Date*.
     - Real-time search filter by ID, name, or locality.
  4. **Employees (Collector Directory)**:
     - Tabular registry displaying: *Collector ID (`COL-XXXX`), Name, Gender, Phone Number, Email ID, Assigned Area, Tasks Assigned, Tasks Cleared, and Digital Coins Earned*.
     - Search filter by collector name, ID, or area.
     - **"+ Add Collector" Modal**: Register new municipal waste collectors and assign areas with automatic `COL-XXXX` generation.

---

## 📂 Project Architecture

```
d:\Anti_gravity Workspace\
├── app.py                     # Flask application server & API routes
├── database.py                # SQLite schema, unique ID generators, seed data
├── test_system.py             # End-to-end automated test suite
├── create_placeholders.py     # Vector graphics generation script
├── requirements.txt           # Python dependency specifications
├── ecoclean.db                # SQLite database
├── static/
│   ├── css/
│   │   └── style.css          # Design system, badge glows, alert styles
│   ├── js/
│   │   ├── main.js            # Global auth, toast alerts, notifications dropdown
│   │   ├── user.js            # Citizen portal (reporting, 48h SLA, badges, profile)
│   │   ├── collector.js       # Collector portal (progress bar, photo proof, coins)
│   │   └── admin.js           # Admin portal (KPIs, 4-color area alerts, tables)
│   ├── images/                # Sample vector placeholders
│   └── uploads/               # User-submitted & collector-verified photos
└── templates/
    ├── base.html              # Base HTML template with navbar and notifications
    ├── index.html             # Landing page with 3-role portal cards
    ├── login.html             # Multi-tab login & registration interface
    ├── user_dashboard.html    # User portal (5 options)
    ├── collector_dashboard.html # Collector portal (3 options)
    └── admin_dashboard.html   # Admin central console (4 options)
```
