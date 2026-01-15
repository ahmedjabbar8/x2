import sqlite3
import hashlib
import os

DB_NAME = "system.db"

def init_db():
    """Initialize the database with users table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Patients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            en_name TEXT,
            age INTEGER,
            dob TEXT,
            gender TEXT,
            phone TEXT,
            governorate TEXT,
            city TEXT,
            doctor TEXT,
            nid TEXT,
            address TEXT,
            category TEXT,
            reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Minor Migrations
    try: cursor.execute("ALTER TABLE patients ADD COLUMN age INTEGER");
    except: pass
    try: cursor.execute("ALTER TABLE patients ADD COLUMN nid TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE patients ADD COLUMN address TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE patients ADD COLUMN category TEXT DEFAULT 'Normal'");
    except: pass
    try: cursor.execute("ALTER TABLE patients ADD COLUMN reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP");
    except: pass

    # Lab Requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            test_type TEXT,
            status TEXT DEFAULT 'Pending Payment',
            result TEXT,
            normal_range TEXT,
            machine_id TEXT,
            validation_status TEXT DEFAULT 'Pending Verification', -- Pending Verification, Verified
            verified_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    try: cursor.execute("ALTER TABLE lab_requests ADD COLUMN result TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE lab_requests ADD COLUMN normal_range TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE lab_requests ADD COLUMN machine_id TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE lab_requests ADD COLUMN validation_status TEXT DEFAULT 'Pending Verification'");
    except: pass
    try: cursor.execute("ALTER TABLE lab_requests ADD COLUMN verified_by TEXT");
    except: pass

    # Radiology Requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rad_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            scan_type TEXT,
            status TEXT DEFAULT 'Pending Payment',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    try: cursor.execute("ALTER TABLE rad_requests ADD COLUMN report TEXT");
    except: pass

    # Invoices (Accounting)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            amount REAL,
            discount_amount REAL DEFAULT 0,
            discount_reason TEXT,
            status TEXT DEFAULT 'Unpaid', -- Unpaid, Paid, Refunded
            description TEXT,
            refund_reason TEXT,
            paid_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    
    # Migrations for invoices
    try: cursor.execute("ALTER TABLE invoices ADD COLUMN discount_amount REAL DEFAULT 0");
    except: pass
    try: cursor.execute("ALTER TABLE invoices ADD COLUMN discount_reason TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE invoices ADD COLUMN refund_reason TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE invoices ADD COLUMN paid_at TIMESTAMP");
    except: pass

    # Archives (Generic storage for past events)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            record_type TEXT, -- Registration, Lab, X-ray, Invoice
            details TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    
    # Pharmacy Requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pharmacy_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            medicine_details TEXT,
            status TEXT DEFAULT 'Pending Payment', -- Pending Payment, Paid (Ready), Dispensed
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    
    # Waiting Room
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waiting_room (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            status TEXT DEFAULT 'Waiting', -- Waiting, Processing, Done
            priority_level TEXT DEFAULT 'Green', -- Red (Critical), Yellow (Urgent), Green (Normal)
            arrived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    try: cursor.execute("ALTER TABLE waiting_room ADD COLUMN priority_level TEXT DEFAULT 'Green'");
    except: pass

    # Appointments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_name TEXT,
            visit_date TEXT, -- YYYY-MM-DD
            visit_time TEXT, -- HH:MM
            reason TEXT,
            diagnosis TEXT,
            prescription TEXT,
            status TEXT DEFAULT 'Scheduled', -- Scheduled, Completed, Cancelled
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    ''')
    try: cursor.execute("ALTER TABLE appointments ADD COLUMN visit_time TEXT"); 
    except: pass

    # Triage Records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS triage_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            appointment_id INTEGER,
            weight TEXT,
            height TEXT,
            blood_pressure TEXT,
            temperature TEXT,
            heart_rate TEXT,
            spo2 TEXT,
            gcs INTEGER,
            pain_scale INTEGER,
            esi_level INTEGER,
            bmi REAL,
            main_complaint TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(appointment_id) REFERENCES appointments(id)
        )
    ''')
    try: cursor.execute("ALTER TABLE triage_records ADD COLUMN spo2 TEXT");
    except: pass
    try: cursor.execute("ALTER TABLE triage_records ADD COLUMN gcs INTEGER");
    except: pass
    try: cursor.execute("ALTER TABLE triage_records ADD COLUMN pain_scale INTEGER");
    except: pass
    try: cursor.execute("ALTER TABLE triage_records ADD COLUMN esi_level INTEGER");
    except: pass
    try: cursor.execute("ALTER TABLE triage_records ADD COLUMN bmi REAL");
    except: pass
    try: cursor.execute("ALTER TABLE triage_records ADD COLUMN main_complaint TEXT");
    except: pass
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            category TEXT DEFAULT 'General'
        )
    ''')
    try: cursor.execute("ALTER TABLE settings ADD COLUMN category TEXT DEFAULT 'General'");
    except: pass
    
    # Check if admin exists, if not create default admin
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ("admin", pw_hash, "admin"))
    
    # Add default users for various roles
    default_users = [
        ("ali_doc", "doc123", "doctor"),
        ("sara_doc", "doc123", "doctor"),
        ("reception", "123", "registration"),
        ("lab", "123", "lab"),
    ]
    for username, password, role in default_users:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                           (username, pw_hash, role))
    
    # Drug Interactions (AI Assistant Seed Data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_interactions (
            drug_a TEXT,
            drug_b TEXT,
            severity TEXT, -- High, Moderate, Low
            description TEXT,
            PRIMARY KEY (drug_a, drug_b)
        )
    ''')
    
    # Seed common interactions
    cursor.execute("INSERT OR IGNORE INTO drug_interactions VALUES ('Aspirin', 'Warfarin', 'High', 'Increased risk of bleeding')")
    cursor.execute("INSERT OR IGNORE INTO drug_interactions VALUES ('Sildenafill', 'Nitroglycerin', 'High', 'Severe drop in blood pressure')")
    cursor.execute("INSERT OR IGNORE INTO drug_interactions VALUES ('Simvastatin', 'Clarithromycin', 'Moderate', 'Increased risk of muscle damage')")

    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value, category='General'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)", (key, value, category))
    conn.commit()
    conn.close()

def get_settings_by_category(category):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}

def get_user(username):
    """Fetch user by username."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    user = dict(row) if row else None
    conn.close()
    return user

def add_user(username, password, role="user"):
    """Add a new user to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       (username, pw_hash, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_doctors():
    """Fetch all users with role 'admin' or 'doctor' to show in dropdown."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users") 
    rows = cursor.fetchall()
    conn.close()
    return [r['username'] for r in rows]

# --- Helper Functions for Modules ---

def add_patient(name, en_name, dob, gender, phone, governorate, city, doctor, nid="", address="", category="Normal"):
    # Calculate Age from DOB
    age = 0
    if dob:
        try:
            from datetime import datetime
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except:
            age = 0

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (name, en_name, age, dob, gender, phone, governorate, city, doctor, nid, address, category) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, en_name, age, dob, gender, phone, governorate, city, doctor, nid, address, category))
    pid = cursor.lastrowid
    
    # Log the registration
    cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                   (pid, 'Registration', f'Patient Registered: {name}'))
    
    # Default Registration Fee
    cursor.execute("INSERT INTO invoices (patient_id, amount, description) VALUES (?, ?, ?)", 
                   (pid, 25000, "Registration Fee"))
    
    conn.commit()
    conn.close()
    return pid

def update_patient(pid, name, en_name, dob, gender, phone, governorate, city, doctor, nid="", address="", category="Normal"):
    # Recalculate Age
    age = 0
    if dob:
        try:
            from datetime import datetime
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except:
            pass

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patients 
        SET name=?, en_name=?, age=?, dob=?, gender=?, phone=?, governorate=?, city=?, doctor=?, nid=?, address=?, category=?
        WHERE id=?
    """, (name, en_name, age, dob, gender, phone, governorate, city, doctor, nid, address, category, pid))
    
    cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                   (pid, 'Update', f'Patient details updated: {name}'))
    
    conn.commit()
    conn.close()

def delete_patient(pid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM patients WHERE id=?", (pid,))
    row = cursor.fetchone()
    name = row[0] if row else "Unknown"
    cursor.execute("DELETE FROM patients WHERE id=?", (pid,))
    cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                   (pid, 'Deletion', f'Patient record deleted: {name}'))
    conn.commit()
    conn.close()
    return True

def get_all_patients():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_today_registrations():
    """Fetch patients registered on the current date."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # SQLITE DATE('now') matches YYYY-MM-DD
    cursor.execute("SELECT * FROM patients WHERE DATE(reg_date) = DATE('now') ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_unbooked_patients_today():
    """Fetch patients registered today who DON'T have an appointment yet."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM patients 
        WHERE DATE(reg_date) = DATE('now')
        AND id NOT IN (SELECT patient_id FROM appointments WHERE visit_date = DATE('now'))
        ORDER BY id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def add_lab_request(patient_id, test_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create request with 'Pending Payment' status
    cursor.execute("INSERT INTO lab_requests (patient_id, test_type, status) VALUES (?, ?, ?)", (patient_id, test_type, 'Pending Payment'))
    
    # Create Invoice
    cursor.execute("INSERT INTO invoices (patient_id, amount, description) VALUES (?, ?, ?)", 
                   (patient_id, 15000, f"Lab: {test_type}")) # Example pricing
    
    conn.commit()
    conn.close()

def get_pending_labs():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, p.name as patient_name 
        FROM lab_requests l 
        JOIN patients p ON l.patient_id = p.id 
        WHERE l.status = 'Pending'
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def complete_lab(req_id, result, normal_range=None, machine_id=None):
    """Called by Lab Tech or Machine interface. Sets result but needs verification."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lab_requests 
        SET result = ?, normal_range = ?, machine_id = ?, validation_status = 'Pending Verification'
        WHERE id = ?
    """, (result, normal_range, machine_id, req_id))
    
    # Check for Critical Values (Panic Limits) - Simple logic for Demo
    try:
        val = float(result.split()[0]) # Assuming numerical result first
        if val > 400 or val < 40: # Example panic limits for Glucose
             # In a real app, this would trigger a system-wide socket alert or SMS
             cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES ((SELECT patient_id FROM lab_requests WHERE id=?), ?, ?)",
                            (req_id, 'CRITICAL ALERT', f'LAB RESULT CRITICAL: {result}'))
    except: pass

    conn.commit()
    conn.close()

def certify_lab_result(req_id, validator_name):
    """Called by Lab Director to certify and move to 'Completed'."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lab_requests 
        SET status = 'Completed', validation_status = 'Verified', verified_by = ? 
        WHERE id = ?
    """, (validator_name, req_id))
    
    # Get details for archive
    cursor.execute("SELECT patient_id, test_type, result FROM lab_requests WHERE id = ?", (req_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                       (row[0], 'Lab', f'Test {row[1]} Certified: {row[2]}'))
        
    conn.commit()
    conn.close()

def get_pending_verification_labs():
    """Fetch labs that have results but are not yet verified by a director."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, p.name as patient_name 
        FROM lab_requests l 
        JOIN patients p ON l.patient_id = p.id 
        WHERE l.validation_status = 'Pending Verification' AND l.result IS NOT NULL
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def check_drug_interactions(drugs):
    """AI Assistant: Check for interactions between a list of medications."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    conflicts = []
    import itertools
    for d1, d2 in itertools.combinations(drugs, 2):
        cursor.execute("SELECT * FROM drug_interactions WHERE (drug_a = ? AND drug_b = ?) OR (drug_a = ? AND drug_b = ?)", (d1, d2, d2, d1))
        row = cursor.fetchone()
        if row:
            conflicts.append({'drug_a': d1, 'drug_b': d2, 'severity': row[2], 'description': row[3]})
    conn.close()
    return conflicts

def add_rad_request(patient_id, scan_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create request with 'Pending Payment' status
    cursor.execute("INSERT INTO rad_requests (patient_id, scan_type, status) VALUES (?, ?, ?)", (patient_id, scan_type, 'Pending Payment'))
    
    # Create Invoice
    cursor.execute("INSERT INTO invoices (patient_id, amount, description) VALUES (?, ?, ?)", 
                   (patient_id, 30000, f"Radiology: {scan_type}")) # Example pricing
    
    conn.commit()
    conn.close()

def get_pending_rads():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, p.name as patient_name 
        FROM rad_requests r 
        JOIN patients p ON r.patient_id = p.id 
        WHERE r.status = 'Pending'
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def complete_rad(req_id, report):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE rad_requests SET status = 'Completed', report = ? WHERE id = ?", (report, req_id))
    
    # Archive
    cursor.execute("SELECT patient_id, scan_type FROM rad_requests WHERE id = ?", (req_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                       (row[0], 'Radiology', f'Scan {row[1]} completed. Report: {report}'))
    
    conn.commit()
    conn.close()

def add_invoice(patient_id, amount, description, appt_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invoices (patient_id, amount, description) VALUES (?, ?, ?)", 
                   (patient_id, amount, description))
    conn.commit()
    conn.close()

def add_pharmacy_request(patient_id, medicine_details, amount=5000):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create pharmacy request
    cursor.execute("INSERT INTO pharmacy_requests (patient_id, medicine_details, amount) VALUES (?, ?, ?)", 
                   (patient_id, medicine_details, amount))
    
    # Create Invoice (Pharmacy payment is handled at pharmacy, but we track it)
    cursor.execute("INSERT INTO invoices (patient_id, amount, description) VALUES (?, ?, ?)", 
                   (patient_id, amount, f"Pharmacy: {medicine_details[:30]}..."))
    
    conn.commit()
    conn.close()

def get_pending_pharmacy():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pr.*, p.name as patient_name 
        FROM pharmacy_requests pr 
        JOIN patients p ON pr.patient_id = p.id 
        WHERE pr.status IN ('Pending Payment', 'Paid')
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def dispense_medicine(req_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE pharmacy_requests SET status = 'Dispensed' WHERE id = ?", (req_id,))
    
    # Archive
    cursor.execute("SELECT patient_id, medicine_details FROM pharmacy_requests WHERE id = ?", (req_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                       (row[0], 'Pharmacy', f'Medication dispensed: {row[1]}'))
        
    conn.commit()
    conn.close()

def get_unpaid_invoices():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name as patient_name 
        FROM invoices i 
        JOIN patients p ON i.patient_id = p.id 
        WHERE i.status = 'Unpaid'
        ORDER BY i.created_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_patient_invoices(patient_id):
    """Fetch all invoices (paid, unpaid, refunded) for a single patient."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM invoices 
        WHERE patient_id = ? 
        ORDER BY created_at DESC
    """, (patient_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_paid_invoices_by_date(date_str):
    """Fetch paid invoices for a specific date (YYYY-MM-DD)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name as patient_name 
        FROM invoices i 
        JOIN patients p ON i.patient_id = p.id 
        WHERE i.status = 'Paid' AND DATE(i.paid_at) = ?
        ORDER BY i.paid_at DESC
    """, (date_str,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def pay_invoice(inv_id, discount=0, reason=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE invoices 
        SET status = 'Paid', discount_amount = ?, discount_reason = ?, paid_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (discount, reason, inv_id))
    
    # Get Invoice Details
    cursor.execute("SELECT patient_id, amount, description FROM invoices WHERE id = ?", (inv_id,))
    row = cursor.fetchone()
    
    if row:
        pid, amount, desc = row
        final_amt = amount - discount
        cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                       (pid, 'Accounting', f'Invoice Paid: {final_amt} IQD (Disc: {discount})'))
        
        # --- WORKFLOW AUTOMATION ---
        if "Registration" in desc or "Consultation" in desc:
            add_to_waiting_room_db(cursor, pid, 'Ready for Triage')
            
        elif "Lab" in desc:
            cursor.execute("""
                UPDATE lab_requests SET status = 'Pending' 
                WHERE patient_id = ? AND status = 'Pending Payment'
            """, (pid,))
            
        elif "Radiology" in desc:
            cursor.execute("""
                UPDATE rad_requests SET status = 'Pending' 
                WHERE patient_id = ? AND status = 'Pending Payment'
            """, (pid,))
            
        elif "Pharmacy" in desc:
            cursor.execute("""
                UPDATE pharmacy_requests SET status = 'Paid' 
                WHERE patient_id = ? AND status = 'Pending Payment'
            """, (pid,))

    conn.commit()
    conn.close()

def refund_invoice(inv_id, reason):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE invoices 
        SET status = 'Refunded', refund_reason = ? 
        WHERE id = ?
    """, (reason, inv_id))
    
    cursor.execute("SELECT patient_id, (amount - discount_amount) FROM invoices WHERE id = ?", (inv_id,))
    row = cursor.fetchone()
    if row:
        pid, amt = row
        cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                       (pid, 'Accounting', f'Invoice Refunded: {amt} IQD. Reason: {reason}'))
    
    conn.commit()
    conn.close()

def get_financial_report(start_date, end_date):
    """Summarize income within a date range with departmental breakdown."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Basic Totals
    cursor.execute("""
        SELECT 
            COUNT(*) as total_invoices,
            COALESCE(SUM(amount), 0) as gross_total,
            COALESCE(SUM(discount_amount), 0) as total_discounts,
            COALESCE(SUM(amount - discount_amount), 0) as net_income
        FROM invoices 
        WHERE status = 'Paid' AND DATE(paid_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    report = dict(cursor.fetchone())
    
    # Departmental Breakdown
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN description LIKE '%Registration%' OR description LIKE '%Consultation%' THEN (amount - discount_amount) ELSE 0 END) as reg_income,
            SUM(CASE WHEN description LIKE '%Lab%' THEN (amount - discount_amount) ELSE 0 END) as lab_income,
            SUM(CASE WHEN description LIKE '%Radiology%' OR description LIKE '%Scan%' THEN (amount - discount_amount) ELSE 0 END) as rad_income,
            SUM(CASE WHEN description LIKE '%Pharmacy%' THEN (amount - discount_amount) ELSE 0 END) as pharmacy_income
        FROM invoices 
        WHERE status = 'Paid' AND DATE(paid_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    breakdown = dict(cursor.fetchone())
    report['breakdown'] = {
        'Registration': breakdown['reg_income'] or 0,
        'Laboratory': breakdown['lab_income'] or 0,
        'Radiology': breakdown['rad_income'] or 0,
        'Pharmacy': breakdown['pharmacy_income'] or 0
    }
    
    conn.close()
    return report

def get_archives():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.name as patient_name 
        FROM archives a 
        JOIN patients p ON a.patient_id = p.id 
        ORDER BY a.date DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def add_to_waiting_room_db(cursor, patient_id, status='Waiting'):
    # Internal helper to add to waiting room reusing a cursor
    cursor.execute("SELECT id FROM waiting_room WHERE patient_id = ? AND status != 'Done'", (patient_id,))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO waiting_room (patient_id, status) VALUES (?, ?)", (patient_id, status))
    return True

def add_to_waiting_room(patient_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if add_to_waiting_room_db(cursor, patient_id):
        conn.commit()
        ret = True
    else:
        ret = False
    conn.close()
    return ret

def get_waiting_list():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT w.*, p.name as patient_name, p.age, p.gender 
        FROM waiting_room w
        JOIN patients p ON w.patient_id = p.id 
        WHERE w.status != 'Done'
        ORDER BY w.arrived_at ASC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def process_waiting(wait_id, new_status='Done'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE waiting_room SET status = ? WHERE id = ?", (new_status, wait_id,))
    conn.commit()
    conn.close()



def add_appointment(patient_id, doctor, date, reason, visit_time="10:00"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Create Appointment
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_name, visit_date, visit_time, reason) 
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, doctor, date, visit_time, reason))
    
    # 2. Auto-Create Invoice for Consultation
    # In a real app, fee would come from settings or doctor rate
    CONSULTATION_FEE = 25000 
    cursor.execute("INSERT INTO invoices (patient_id, amount, description) VALUES (?, ?, ?)", 
                   (patient_id, CONSULTATION_FEE, f"Consultation with Dr. {doctor}"))
    
    conn.commit()
    conn.close()

def get_appointments():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.name as patient_name 
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id 
        ORDER BY a.visit_date ASC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_appointments_by_date(date_str):
    """Fetch appointments for a specific date (YYYY-MM-DD)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.name as patient_name, p.phone, p.gender
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id 
        WHERE a.visit_date = ?
        ORDER BY a.visit_time ASC
    """, (date_str,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def complete_appointment(appt_id, diagnosis, prescription):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments 
        SET status = 'Completed', diagnosis = ?, prescription = ? 
        WHERE id = ?
    """, (diagnosis, prescription, appt_id))
    
    # Archive
    cursor.execute("SELECT patient_id, doctor_name FROM appointments WHERE id = ?", (appt_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("INSERT INTO archives (patient_id, record_type, details) VALUES (?, ?, ?)",
                       (row[0], 'Doctor Visit', f'Seen by Dr. {row[1]}. Dx: {diagnosis}'))
    conn.commit()
    conn.close()

def add_triage_record(patient_id, weight, height, bp, temp, hr, priority='Green', spo2=None, gcs=15, pain=0, esi=5, bmi=0, complaint="", update_status=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO triage_records (patient_id, weight, height, blood_pressure, temperature, heart_rate, spo2, gcs, pain_scale, esi_level, bmi, main_complaint)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, weight, height, bp, temp, hr, spo2, gcs, pain, esi, bmi, complaint))
    
    if update_status:
        cursor.execute("""
            UPDATE waiting_room 
            SET status = 'Triaged (Ready for Doctor)', priority_level = ? 
            WHERE patient_id = ? AND status != 'Done'
        """, (priority, patient_id))
    
    conn.commit()
    conn.close()

def get_latest_triage(patient_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM triage_records WHERE patient_id = ? ORDER BY created_at DESC LIMIT 1", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def route_patient_to_doctor(patient_id, priority='Green'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE waiting_room 
        SET status = 'Waiting for Doctor', priority_level = ? 
        WHERE patient_id = ? AND status != 'Done'
    """, (priority, patient_id))
    conn.commit()
    conn.close()

def get_patient_vitals(patient_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM triage_records WHERE patient_id = ? ORDER BY created_at DESC LIMIT 1", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_doctor_queue_count(doctor, date):
    """Count existing appointments for a doctor on a specific date."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE doctor_name = ? AND visit_date = ?", (doctor, date))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_doctors_list():
    """Returns a list of usernames who are doctors."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE role = 'Doctor'")
    doctors = [r[0] for r in cursor.fetchall()]
    conn.close()
    return doctors or ['Dr. Ahmed', 'Dr. Sarah', 'Dr. Ali'] # Fallback for demo

def clear_all_clinical_data():
    """Wipe all patient-related data but keep users/accounts."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    tables = [
        'patients', 'lab_requests', 'rad_requests', 'invoices', 
        'archives', 'waiting_room', 'appointments', 'triage_records'
    ]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        # Reset autoincrement
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
    conn.commit()
    conn.close()
    return True

def get_dashboard_stats():
    """Fetch counts for the dashboard pathway."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    stats = {}
    
    # Scheduled / Accounting (Pending Registration or Consultation payment)
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Unpaid' AND DATE(created_at) = DATE('now')")
    stats['scheduled'] = cursor.fetchone()[0]
    
    # Triage (Ready for Triage)
    cursor.execute("SELECT COUNT(*) FROM waiting_room WHERE status = 'Ready for Triage' AND DATE(arrived_at) = DATE('now')")
    stats['triage'] = cursor.fetchone()[0]
    
    # Doctor (Triaged / Ready for Doctor)
    cursor.execute("SELECT COUNT(*) FROM waiting_room WHERE status = 'Triaged (Ready for Doctor)' AND DATE(arrived_at) = DATE('now')")
    stats['doctor'] = cursor.fetchone()[0]
    
    # Exams (Pending Labs + Pending Radiology)
    cursor.execute("SELECT COUNT(*) FROM lab_requests WHERE status = 'Pending' AND DATE(created_at) = DATE('now')")
    lab_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM rad_requests WHERE status = 'Pending' AND DATE(created_at) = DATE('now')")
    rad_count = cursor.fetchone()[0]
    stats['exams'] = lab_count + rad_count
    
    # Pharmacy
    cursor.execute("SELECT COUNT(*) FROM pharmacy_requests WHERE status = 'Pending Payment' AND DATE(created_at) = DATE('now')")
    stats['pharmacy'] = cursor.fetchone()[0]    
    # Done (Completed appointments today)
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Completed' AND visit_date = DATE('now')")
    stats['done'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

