import pyodbc
from flask import current_app
from datetime import datetime

def get_db_connection():
    conn_str = current_app.config.get('DB_CONNECTION_STRING', 
        'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=BloodLink;Trusted_Connection=yes;')
    conn = pyodbc.connect(conn_str)
    return conn

# --- Auth Queries ---

def get_user_by_email_password(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM [User] WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_name_by_role_id(role, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    name = None
    if role == 'Manager':
        cursor.execute("SELECT name FROM Manager WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row: name = row.name
    elif role == 'Donor':
        cursor.execute("SELECT name FROM Donor WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row: name = row.name
    elif role == 'Recipient':
        cursor.execute("SELECT name FROM Recipient WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row: name = row.name
    conn.close()
    return name

def create_user(email, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO [User] (email, password, role) OUTPUT INSERTED.id VALUES (?, ?, ?)", (email, password, role))
    user_id = cursor.fetchone()[0]
    conn.commit() # Commit here or let caller handle? Caller handles transaction usually, but for simple functions we can commit.
    # Actually, for registration transaction (User + Role), we need to keep connection open.
    # Let's return connection and cursor or handle transaction inside a wrapper?
    # For simplicity in this refactor, let's keep it simple. 
    # The register route does a transaction. We might need a 'create_user_transaction' or similar.
    # OR we pass the cursor to these functions.
    # Let's stick to the pattern: "Functions perform atomic operations or we pass connection".
    # Given the existing code structure, passing connection is better for transactions.
    # BUT, to keep it simple for the user's request "queries in a file", let's make functions that take a cursor optionally, or manage their own.
    # For the registration transaction, let's create a specific function `register_user_transaction`.
    conn.close()
    return user_id

def get_blood_type_id(type_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bloodtype_id FROM Blood_Type WHERE type = ?", (type_str,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def register_user_transaction(email, password, role, name, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO [User] (email, password, role) OUTPUT INSERTED.id VALUES (?, ?, ?)", (email, password, role))
        user_id = cursor.fetchone()[0]
        
        blood_type_id = None
        if kwargs.get('blood_type'):
            blood_type_id = get_blood_type_id(kwargs.get('blood_type'))

        if role == 'Donor':
            age = None
            dob = None
            if kwargs.get('dob'):
                dob = datetime.strptime(kwargs.get('dob'), '%Y-%m-%d').date()
                today = datetime.today().date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            cursor.execute("""
                INSERT INTO Donor (name, user_id, bloodtype, DOB, age, area, number) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, user_id, blood_type_id, dob, age, kwargs.get('area'), kwargs.get('number')))
        elif role == 'Recipient':
            cursor.execute("INSERT INTO Recipient (name, user_id, bloodtype, area) VALUES (?, ?, ?, ?)", (name, user_id, blood_type_id, kwargs.get('area')))
        elif role == 'Manager':
            cursor.execute("INSERT INTO Manager (name, user_id) VALUES (?, ?)", (name, user_id))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# --- Manager Queries ---

def get_inventory_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bt.type, SUM(s.units) as total_units
        FROM Stock s
        JOIN Donation_Completed dc ON s.donation_id = dc.id
        JOIN Blood_Type bt ON dc.blood_type = bt.bloodtype_id
        GROUP BY bt.type
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_donors():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.name, bt.type, d.number, d.area, d.availability
        FROM Donor d
        JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_donor_details_by_id(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.name, bt.type 
        FROM Donor d 
        JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id 
        WHERE d.id = ?
    """, (donor_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def submit_donation_transaction(donor_id, volume, is_exchange):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT bloodtype FROM Donor WHERE id = ?", (donor_id,))
        blood_type_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO Donation_Completed (donor_id, units, blood_type, is_exchange, donation_date)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, GETDATE())
        """, (donor_id, volume, blood_type_id, is_exchange))
        donation_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO Stock (units, donation_id)
            VALUES (?, ?)
        """, (volume, donation_id))
        
        cursor.execute("""
            INSERT INTO Donor_History (donor_id, [date], unit)
            VALUES (?, GETDATE(), ?)
        """, (donor_id, volume))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_all_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, rec.name, bt.type, r.units_required, r.status, r.date_requested
        FROM Request r
        JOIN Recipient rec ON r.recipient_id = rec.id
        JOIN Blood_Type bt ON r.blood_type = bt.bloodtype_id
        ORDER BY r.date_requested DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def approve_request_transaction(request_id, manager_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM Manager WHERE user_id = ?", (manager_user_id,))
        manager_id = cursor.fetchone()[0]
        
        cursor.execute("""
            UPDATE Request 
            SET status = 'Approved', approved_by = ? 
            WHERE id = ?
        """, (manager_id, request_id))
        
        cursor.execute("SELECT blood_type FROM Request WHERE id = ?", (request_id,))
        req_blood_type = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT user_id FROM Donor 
            WHERE bloodtype = ? AND availability = 1
        """, (req_blood_type,))
        eligible_donors = cursor.fetchall()
        
        for donor in eligible_donors:
            if donor.user_id:
                cursor.execute("""
                    INSERT INTO Notifications (user_id, message, type)
                    VALUES (?, 'Urgent: Blood needed matching your type!', 'Broadcast')
                """, (donor.user_id,))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def fulfill_request_transaction(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Request SET status = 'Fulfilled', date_fulfilled = GETDATE() WHERE id = ?", (request_id,))
        
        cursor.execute("""
            SELECT r.user_id 
            FROM Request req
            JOIN Recipient r ON req.recipient_id = r.id
            WHERE req.id = ?
        """, (request_id,))
        recipient_user_id = cursor.fetchone()[0]
        
        if recipient_user_id:
            cursor.execute("""
                INSERT INTO Notifications (user_id, message, type)
                VALUES (?, 'Your blood request has been fulfilled. Please come to collect.', 'Collection')
            """, (recipient_user_id,))
            
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# --- Donor Queries ---

def get_donor_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Donor WHERE user_id = ?", (user_id,))
    donor = cursor.fetchone()
    conn.close()
    return donor

def get_donor_history(donor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT units, donation_date, is_exchange 
        FROM Donation_Completed 
        WHERE donor_id = ? 
        ORDER BY donation_date DESC
    """, (donor_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def toggle_donor_availability(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Donor 
            SET availability = CASE WHEN availability = 1 THEN 0 ELSE 1 END 
            OUTPUT INSERTED.availability
            WHERE user_id = ?
        """, (user_id,))
        new_status = cursor.fetchone()[0]
        conn.commit()
        return True, new_status
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# --- Recipient Queries ---

def get_recipient_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Recipient WHERE user_id = ?", (user_id,))
    recipient = cursor.fetchone()
    conn.close()
    return recipient

def get_recipient_requests(recipient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM Request 
        WHERE recipient_id = ? 
        ORDER BY date_requested DESC
    """, (recipient_id,))
    requests = cursor.fetchall()
    conn.close()
    return requests

def create_request_transaction(user_id, units, blood_type_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM Recipient WHERE user_id = ?", (user_id,))
        recipient_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO Request (recipient_id, units_required, blood_type, status)
            VALUES (?, ?, ?, 'Pending')
        """, (recipient_id, units, blood_type_id))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
