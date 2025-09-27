# db.py
"""
Database connection and helper functions for BloodLink Flask app.
"""
import os
import pyodbc
from datetime import datetime

# Get DB config from environment or defaults

def get_db_config():
    server = os.getenv('MSSQL_SERVER', 'localhost\\SQLSERVER')
    database = os.getenv('MSSQL_DATABASE', 'blood')
    driver = os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')
    return driver, server, database

# Create a new DB connection
def get_connection():
    driver, server, database = get_db_config()
    odbc_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes"
    return pyodbc.connect(odbc_str)

# Check DB connectivity (for health check)
def check_db_connectivity():
    try:
        conn = get_connection()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


# Fast user lookup across all user tables
def get_user_by_email(email):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Check all three tables in one go
        queries = [
            ("donor", "SELECT DonorID, Name, Email, Password, Area, LastDonationDate FROM DONOR WHERE Email=?"),
            ("recipient", "SELECT RecipientID, Name, Email, Password, Area, ContactDetails FROM RECIPIENT WHERE Email=?"),
            ("manager", "SELECT ManagerID, Name, Email, Password FROM MANAGER WHERE Email=?")
        ]
        for role, sql in queries:
            cur.execute(sql, (email,))
            row = cur.fetchone()
            if row:
                # Return a unified user dict
                if role == "donor":
                    return {
                        'id': row[0],
                        'role': 'donor',
                        'name': row[1],
                        'email': row[2],
                        'password': row[3],
                        'area': row[4],
                        'last_donation_date': row[5]
                    }
                elif role == "recipient":
                    return {
                        'id': row[0],
                        'role': 'recipient',
                        'name': row[1],
                        'email': row[2],
                        'password': row[3],
                        'area': row[4],
                        'contact_details': row[5]
                    }
                elif role == "manager":
                    return {
                        'id': row[0],
                        'role': 'manager',
                        'name': row[1],
                        'email': row[2],
                        'password': row[3]
                    }
        return None
    finally:
        conn.close()


# Get user by ID and role
def get_user_by_id(user_id, role):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if role == 'donor':
            cur.execute('SELECT DonorID, Name, Email, Password, Area, LastDonationDate FROM DONOR WHERE DonorID=?', (user_id,))
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'role': 'donor',
                    'name': row[1],
                    'email': row[2],
                    'password': row[3],
                    'area': row[4],
                    'last_donation_date': row[5]
                }
        elif role == 'recipient':
            cur.execute('SELECT RecipientID, Name, Email, Password, Area, ContactDetails FROM RECIPIENT WHERE RecipientID=?', (user_id,))
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'role': 'recipient',
                    'name': row[1],
                    'email': row[2],
                    'password': row[3],
                    'area': row[4],
                    'contact_details': row[5]
                }
        elif role == 'manager':
            cur.execute('SELECT ManagerID, Name, Email, Password FROM MANAGER WHERE ManagerID=?', (user_id,))
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'role': 'manager',
                    'name': row[1],
                    'email': row[2],
                    'password': row[3]
                }
        return None
    finally:
        conn.close()

# Registration helpers (donor, recipient, generic)

def insert_donor(name, email, password, area, blood_type, last_donation, contact_details=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT DonorID FROM DONOR WHERE Email=?', (email,))
        if cur.fetchone():
            return False, 'Email already registered.'
        last_donation_date = None
        if last_donation:
            try:
                last_donation_date = datetime.strptime(last_donation, '%Y-%m-%d').date()
            except ValueError:
                return False, 'Invalid last donation date format. Use YYYY-MM-DD.'
        insert_sql = '''
INSERT INTO DONOR (Name, Email, Password, Area, FK_BloodTypeID, LastDonationDate, AvailabilityStatus, IsEligible)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        # For now, set FK_BloodTypeID, AvailabilityStatus, IsEligible to None/True as needed
        cur.execute(insert_sql, (name, email, password, area, None, last_donation_date, 'available', 1))
        conn.commit()
        return True, None
    finally:
        conn.close()


def insert_recipient(name, email, password, area, contact_details):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute('SELECT RecipientID FROM RECIPIENT WHERE Email=?', (email,))
        if cur.fetchone():
            return False, 'Email already registered.'
        insert_sql = '''
INSERT INTO RECIPIENT (Name, Email, Password, Area, ContactDetails)
VALUES (?, ?, ?, ?, ?)'''
        cur.execute(insert_sql, (name, email, password, area, contact_details))
        conn.commit()
        return True, None
    finally:
        conn.close()
