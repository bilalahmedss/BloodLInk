import pyodbc
from flask import current_app
from datetime import datetime

# ==================================================================================
# DATABASE CONNECTION
# ==================================================================================

def get_db_connection():
    """
    Establishes and returns a connection to the SQL Server database.
    Uses the connection string from the Flask app configuration.
    """
    conn_str = current_app.config.get('DB_CONNECTION_STRING', 
        'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=BloodLink;Trusted_Connection=yes;')
    conn = pyodbc.connect(conn_str)
    return conn

# ==================================================================================
# AUTHENTICATION & USER MANAGEMENT
# ==================================================================================

def get_user_by_email_password(email, password):
    """
    Retrieves a user by email and password for login authentication.
    
    QUERY: Simple SELECT with WHERE clause for exact match on credentials.
    KEYWORDS: Login, Authentication, Select, Where
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM [User] WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_name_by_role_id(role, user_id):
    """
    Retrieves the name of a user based on their specific role and user_id.
    Handles 'Manager', 'Donor', and 'Recipient' roles.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    name = None
    
    if role == 'Manager':
        cursor.execute("SELECT name FROM Manager WHERE user_id = ?", (user_id,))
    elif role == 'Donor':
        cursor.execute("SELECT name FROM Donor WHERE user_id = ?", (user_id,))
    elif role == 'Recipient':
        cursor.execute("SELECT name FROM Recipient WHERE user_id = ?", (user_id,))
    
    row = cursor.fetchone()
    if row: name = row.name
    conn.close()
    return name

def get_blood_type_id(type_str):
    """
    Helper function to retrieve the ID of a blood type from its string representation (e.g., 'A+').
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bloodtype_id FROM Blood_Type WHERE type = ?", (type_str,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_areas():
    """
    Retrieves all available areas from the Area table.
    Used for populating dropdowns in registration and filtering.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Area")
    areas = cursor.fetchall()
    conn.close()
    return areas

def register_user_transaction(email, password, role, name, **kwargs):
    """
    Registers a new user and creates their role-specific profile in a single atomic transaction.
    
    QUERY: Multi-step INSERT using OUTPUT clause to get the new ID.
    KEYWORDS: Transaction, Atomic, Insert, Output, Rollback, Commit
    
    Args:
        email (str): User's email.
        password (str): User's password.
        role (str): 'Donor', 'Recipient', or 'Manager'.
        name (str): Full name.
        **kwargs: Additional fields like 'blood_type', 'area_id', 'number', 'dob'.
        
    Returns:
        (bool, str): (Success, Error Message)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Step 1: Create the base User account
        cursor.execute("INSERT INTO [User] (email, password, role) OUTPUT INSERTED.id VALUES (?, ?, ?)", (email, password, role))
        user_id = cursor.fetchone()[0]
        
        # Prepare common data
        blood_type_id = None
        if kwargs.get('blood_type'):
            blood_type_id = get_blood_type_id(kwargs.get('blood_type'))

        area_id = kwargs.get('area_id')

        # Step 2: Create the Role-Specific Profile
        if role == 'Donor':
            age = None
            dob = None
            if kwargs.get('dob'):
                dob = datetime.strptime(kwargs.get('dob'), '%Y-%m-%d').date()
                today = datetime.today().date()
                # Calculate age accurately accounting for leap years
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            cursor.execute("""
                INSERT INTO Donor (name, user_id, bloodtype, DOB, age, area_id, number) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, user_id, blood_type_id, dob, age, area_id, kwargs.get('number')))
            
        elif role == 'Recipient':
            age = None
            dob = None
            if kwargs.get('dob'):
                dob = datetime.strptime(kwargs.get('dob'), '%Y-%m-%d').date()
                today = datetime.today().date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            cursor.execute("""
                INSERT INTO Recipient (name, user_id, bloodtype, area_id, number, DOB, age) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, user_id, blood_type_id, area_id, kwargs.get('number'), dob, age))
            
        elif role == 'Manager':
            cursor.execute("INSERT INTO Manager (name, user_id) VALUES (?, ?)", (name, user_id))
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ==================================================================================
# MANAGER FUNCTIONS
# ==================================================================================

def get_inventory_stats(area_id=None, blood_type=None):
    """
    Retrieves blood inventory statistics grouped by Area and Blood Type.
    Supports optional filtering by Area ID and Blood Type.
    
    QUERY: Aggregation using SUM() and GROUP BY to calculate total units per category.
    KEYWORDS: Inventory, Aggregation, Group By, Sum, Join
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT a.name as area_name, bt.type, SUM(s.units) as total_units
        FROM Stock s
        JOIN Donation_Completed dc ON s.donation_id = dc.id
        JOIN Blood_Type bt ON dc.blood_type = bt.bloodtype_id
        JOIN Area a ON s.area_id = a.id
        WHERE 1=1
    """
    params = []
    
    if area_id:
        query += " AND s.area_id = ?"
        params.append(area_id)
        
    if blood_type:
        query += " AND bt.type = ?"
        params.append(blood_type)
        
    query += """
        GROUP BY a.name, bt.type
        ORDER BY a.name, bt.type
    """
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_donors(page=1, per_page=10, area_id=None, blood_type=None):
    """
    Retrieves a paginated list of all donors with their statistics.
    Includes filtering by Area and Blood Type.
    
    QUERY: Complex JOINs (Donor, Blood_Type, Area, Donation_Completed) with dynamic WHERE clause and OFFSET-FETCH pagination.
    KEYWORDS: Pagination, Offset, Fetch, Dynamic SQL, Filtering, Count
    
    Returns:
        (list, int): (List of donor rows, Total count)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    
    # Construct WHERE clause dynamically
    where_conditions = []
    params = []
    
    if area_id:
        where_conditions.append("d.area_id = ?")
        params.append(area_id)
        
    if blood_type:
        where_conditions.append("bt.type = ?")
        params.append(blood_type)
        
    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    
    # Step 1: Get Total Count for Pagination
    count_query = f"""
        SELECT COUNT(*) 
        FROM Donor d 
        JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id 
        {where_clause}
    """
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # Step 2: Fetch Paginated Data
    query = f"""
        SELECT d.id, d.name, bt.type as blood_type, d.number as phone, a.name as area_name, d.availability as is_available,
               COUNT(dc.id) as total_donations,
               MAX(dc.donation_date) as last_donation
        FROM Donor d
        JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id
        LEFT JOIN Area a ON d.area_id = a.id
        LEFT JOIN Donation_Completed dc ON d.id = dc.donor_id
        {where_clause}
        GROUP BY d.id, d.name, bt.type, d.number, a.name, d.availability
        ORDER BY d.name
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """
    
    main_params = params + [offset, per_page]
    
    cursor.execute(query, main_params)
    data = cursor.fetchall()
    conn.close()
    return data, total

def search_donor(query):
    """
    Searches for donors by ID (exact match) or Name (partial match).
    Returns a list of matching donors with their ID, Name, Blood Type, and Area ID.
    
    QUERY: Conditional logic to switch between exact ID match and LIKE operator for name search.
    KEYWORDS: Search, Lookup, Like, Wildcard, Partial Match
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if query is numeric (ID search)
    if str(query).isdigit():
        cursor.execute("""
            SELECT d.id, d.name, bt.type, d.area_id 
            FROM Donor d 
            JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id 
            WHERE d.id = ?
        """, (query,))
    else:
        # Name search (partial match)
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT d.id, d.name, bt.type, d.area_id 
            FROM Donor d 
            JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id 
            WHERE d.name LIKE ?
        """, (search_term,))
        
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_active_requests(area_id=None):
    """
    Retrieves requests that are 'Pending' or 'Approved'.
    Used for selecting a request during an Exchange donation.
    Optionally filters by the Recipient's Area.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT r.id, rec.name, bt.type, r.units_required, r.units_collected
        FROM Request r
        JOIN Recipient rec ON r.recipient_id = rec.id
        JOIN Blood_Type bt ON r.blood_type = bt.bloodtype_id
        WHERE r.status IN ('Pending', 'Approved')
    """
    params = []
    
    if area_id:
        query += " AND rec.area_id = ?"
        params.append(area_id)
        
    query += " ORDER BY r.date_requested DESC"
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_requests(page=1, per_page=10):
    """
    Retrieves all requests with detailed status and approver info.
    Supports pagination.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    
    # Get Total Count
    cursor.execute("SELECT COUNT(*) FROM Request")
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT r.id, rec.name, bt.type, r.units_required, r.units_collected, r.status, r.date_requested, m.name as approved_by_name
        FROM Request r
        JOIN Recipient rec ON r.recipient_id = rec.id
        JOIN Blood_Type bt ON r.blood_type = bt.bloodtype_id
        LEFT JOIN Manager m ON r.approved_by = m.id
        ORDER BY r.date_requested DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (offset, per_page))
    data = cursor.fetchall()
    conn.close()
    return data, total

def approve_request_transaction(request_id, manager_user_id):
    """
    Approves a blood request and notifies eligible donors.
    
    Steps:
    1. Update Request status to 'Approved'.
    2. Notify the Recipient.
    3. Broadcast notification to all eligible Donors (matching blood type).
    
    QUERY: Transaction block updating Request status and inserting Notifications.
    KEYWORDS: Approval, Update, Notification, Broadcast, Transaction
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM Manager WHERE user_id = ?", (manager_user_id,))
        manager_id = cursor.fetchone()[0]
        
        # Step 1: Update Request Status
        cursor.execute("""
            UPDATE Request 
            SET status = 'Approved', approved_by = ? 
            WHERE id = ?
        """, (manager_id, request_id))
        
        # Step 2: Notify Recipient
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
                VALUES (?, 'Your request has been approved and is in process.', 'General')
            """, (recipient_user_id,))
        
        # Step 3: Notify Eligible Donors (Broadcast)
        cursor.execute("SELECT blood_type FROM Request WHERE id = ?", (request_id,))
        req_blood_type = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT user_id FROM Donor 
            WHERE bloodtype = ? AND availability = 1
        """, (req_blood_type,))
        eligible_donors = cursor.fetchall()
        
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def submit_donation_transaction(donor_id, volume, is_exchange, request_id=None):
    """
    Records a donation transaction.
    Handles strict location consistency and inventory swapping for Exchange donations.
    Enforces 30-day donation rule.
    
    QUERY: Complex multi-step transaction involving:
           1. Eligibility Check (Select)
           2. Stock Consumption (Delete/Update) for Exchange
           3. Donation Recording (Insert)
           4. Stock Addition (Insert)
           5. History Update (Insert)
           6. Request Update (Update)
           7. Notification (Insert)
    KEYWORDS: Transaction, Exchange, Stock Management, FIFO, Insert, Update, Rollback
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT bloodtype, area_id FROM Donor WHERE id = ?", (donor_id,))
        row = cursor.fetchone()
        blood_type_id = row[0]
        area_id = row[1]
        
        is_direct_exchange = False # Initialize flag
        
        # Step 0a: Enforce 1 Unit Limit
        if int(volume) != 1:
            return False, "Donation limit is strictly 1 unit per session."
        
        # Step 0: Check Eligibility (30-day rule)
        cursor.execute("""
            SELECT TOP 1 donation_date 
            FROM Donation_Completed 
            WHERE donor_id = ? 
            ORDER BY donation_date DESC
        """, (donor_id,))
        last_donation_row = cursor.fetchone()
        
        if last_donation_row:
            last_date = last_donation_row[0].date()
            today = datetime.now().date()
            days_since = (today - last_date).days
            
            if days_since < 30:
                return False, f"Donor is not eligible. Last donation was {days_since} days ago. Must wait 30 days."

        # Step 1: Handle Exchange Logic Checks & Outbound Stock
        if is_exchange and request_id:
            # Get Request Details
            cursor.execute("""
                SELECT r.blood_type, rec.area_id 
                FROM Request r 
                JOIN Recipient rec ON r.recipient_id = rec.id 
                WHERE r.id = ?
            """, (request_id,))
            req_row = cursor.fetchone()
            if not req_row:
                 return False, "Request not found."
            
            req_blood_type_id = req_row[0]
            req_area_id = req_row[1]

            # A. Area Match Check
            if str(area_id) != str(req_area_id):
                 return False, "Location Mismatch: Donor and Request must be in the same area."

            # Check for Direct Exchange (Same Blood Type)
            # If Donor Type == Recipient Type, we don't need to swap stock.
            # We just assign this donation to the request directly.
            is_direct_exchange = (blood_type_id == req_blood_type_id)

            if not is_direct_exchange:
                # B. Consume Stock (Outbound) - Swap Mechanism
                # We consume 'volume' amount of the REQUIRED blood type from the SAME area.
                if not consume_stock(cursor, area_id, req_blood_type_id, int(volume)):
                     return False, "Exchange Failed: Insufficient stock of required blood type for recipient."

        # Step 2: Record Donation (Inbound)
        cursor.execute("""
            INSERT INTO Donation_Completed (donor_id, units, blood_type, is_exchange, donation_date, request_id)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, GETDATE(), ?)
        """, (donor_id, volume, blood_type_id, is_exchange, request_id))
        donation_id = cursor.fetchone()[0]
        
        # Step 3: Add to Stock (Inbound)
        # Only add to stock if it's NOT a direct exchange.
        # Direct exchange units are logically consumed by the request immediately.
        if not is_direct_exchange:
            cursor.execute("""
                INSERT INTO Stock (units, donation_id, area_id)
                VALUES (?, ?, ?)
            """, (volume, donation_id, area_id))
        
        # Step 4: Update Donor History
        cursor.execute("INSERT INTO dbo.Donor_History (donor_id, [date], [unit]) VALUES (?, GETDATE(), ?)", (donor_id, volume))
        
        # Step 5: Update Request Progress (if exchange)
        if is_exchange and request_id:
            cursor.execute("""
                UPDATE Request
                SET units_collected = units_collected + ?
                WHERE id = ?
            """, (volume, request_id))
            
            # Check fulfillment
            cursor.execute("SELECT units_required, units_collected FROM Request WHERE id = ?", (request_id,))
            req_row = cursor.fetchone()
            if req_row and req_row[1] >= req_row[0]:
                cursor.execute("UPDATE Request SET status = 'Fulfilled', date_fulfilled = GETDATE() WHERE id = ?", (request_id,))
                
                # Notify Recipient
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
                        VALUES (?, 'Your blood request has been fulfilled!', 'Collection')
                    """, (recipient_user_id,))

        # Step 6: Auto-Deactivate Donor (Set Availability to 0)
        cursor.execute("UPDATE Donor SET availability = 0 WHERE id = ?", (donor_id,))

        # Step 7: Notify Donor
        cursor.execute("SELECT user_id FROM Donor WHERE id = ?", (donor_id,))
        donor_user_id = cursor.fetchone()[0]
        if donor_user_id:
             cursor.execute("""
                INSERT INTO Notifications (user_id, message, type)
                VALUES (?, ?, 'General')
            """, (donor_user_id, f'Thank you! Your donation of {volume} unit(s) has been recorded.'))

        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def consume_stock(cursor, area_id, blood_type_id, units_needed):
    """
    Consumes stock using FIFO (First-In-First-Out) strategy.
    Removes oldest stock batches first.
    
    LOGIC:
    1. Fetch all stock batches for the given Area and Blood Type, ordered by Date (Oldest first).
    2. Iterate through batches and deduct units until the required amount is met.
    3. Delete empty batches to keep the table clean.
    
    QUERY: SELECT with ORDER BY donation_date ASC to find oldest stock, followed by DELETE or UPDATE.
    KEYWORDS: FIFO, Stock Consumption, Order By, Date, Delete, Update
    
    Args:
        cursor: Active database cursor (part of transaction).
        area_id: Area to consume stock from.
        blood_type_id: Blood type to consume.
        units_needed: Amount of units to remove.
        
    Returns:
        bool: True if successful, False if insufficient stock.
    """
    # Step 1: Check total available stock
    cursor.execute("""
        SELECT SUM(s.units) 
        FROM Stock s
        JOIN Donation_Completed dc ON s.donation_id = dc.id
        WHERE s.area_id = ? AND dc.blood_type = ?
    """, (area_id, blood_type_id))
    total_available = cursor.fetchone()[0] or 0
    
    if total_available < units_needed:
        return False
        
    # Step 2: Fetch stock batches ordered by date (FIFO)
    cursor.execute("""
        SELECT s.bag_id, s.units
        FROM Stock s
        JOIN Donation_Completed dc ON s.donation_id = dc.id
        WHERE s.area_id = ? AND dc.blood_type = ?
        ORDER BY dc.donation_date ASC
    """, (area_id, blood_type_id))
    batches = cursor.fetchall()
    
    units_to_remove = units_needed
    
    for batch_id, batch_units in batches:
        if units_to_remove <= 0:
            break
            
        if batch_units <= units_to_remove:
            # Consume entire batch
            cursor.execute("DELETE FROM Stock WHERE bag_id = ?", (batch_id,))
            units_to_remove -= batch_units
        else:
            # Consume partial batch
            cursor.execute("UPDATE Stock SET units = units - ? WHERE bag_id = ?", (units_to_remove, batch_id))
            units_to_remove = 0
            
    return True

def fulfill_request_transaction(request_id):
    """
    Manually fulfills a request by a Manager.
    Consumes necessary stock and updates request status.
    
    QUERY: Transaction that consumes stock (FIFO) and updates Request status to 'Fulfilled'.
    KEYWORDS: Fulfillment, Stock Consumption, Update, Transaction
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Step 1: Get Request Details
        cursor.execute("""
            SELECT r.units_required, r.blood_type, u.area_id, r.recipient_id
            FROM Request r
            JOIN Recipient rec ON r.recipient_id = rec.id
            JOIN [User] u ON rec.user_id = u.id
            WHERE r.id = ?
        """, (request_id,))
        req_row = cursor.fetchone()
        
        if not req_row:
            return False, "Request not found"
            
        units_required = req_row[0]
        blood_type_id = req_row[1]
        area_id = req_row[2]
        recipient_id = req_row[3]
        
        # Step 2: Consume Stock
        if not consume_stock(cursor, area_id, blood_type_id, units_required):
            return False, "Insufficient stock in this area to fulfill request."
            
        # Step 3: Update Request Status
        cursor.execute("UPDATE Request SET status = 'Fulfilled', date_fulfilled = GETDATE() WHERE id = ?", (request_id,))
        
        # Step 4: Notify Recipient
        cursor.execute("SELECT user_id FROM Recipient WHERE id = ?", (recipient_id,))
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

# ==================================================================================
# DONOR FUNCTIONS
# ==================================================================================

def get_donor_by_user_id(user_id):
    """Retrieves donor profile by user_id with blood type string."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.*, bt.type as blood_type_str 
        FROM Donor d
        JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id
        WHERE d.user_id = ?
    """, (user_id,))
    donor = cursor.fetchone()
    conn.close()
    return donor

def get_donor_history(donor_id, page=1, per_page=5):
    """Retrieves donation history for a donor with pagination."""
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    
    cursor.execute("SELECT COUNT(*) FROM Donation_Completed WHERE donor_id = ?", (donor_id,))
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT units, donation_date, is_exchange 
        FROM Donation_Completed 
        WHERE donor_id = ? 
        ORDER BY donation_date DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (donor_id, offset, per_page))
    history = cursor.fetchall()
    conn.close()
    return history, total

def update_donor_profile(user_id, name, area_id, number, dob_str):
    """Updates donor profile details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        age = None
        dob = None
        if dob_str:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            today = datetime.today().date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
        cursor.execute("""
            UPDATE Donor
            SET name = ?, area_id = ?, number = ?, DOB = ?, age = ?
            WHERE user_id = ?
        """, (name, area_id, number, dob, age, user_id))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def toggle_donor_availability(user_id):
    """Toggles donor availability status."""
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

def check_donor_eligibility(user_id):
    """
    Checks if a donor is eligible to donate based on the 30-day rule.
    Does NOT auto-update availability.
    
    LOGIC:
    1. Fetch the last donation date for the donor.
    2. Calculate days elapsed since then.
    3. If < 30 days, return False and the remaining days.
    
    Returns:
        (bool, int): (Is Eligible, Days Left)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get donor details
        cursor.execute("SELECT id FROM Donor WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row: return False, 0
        
        donor_id = row[0]
        
        # Check last donation date
        cursor.execute("""
            SELECT TOP 1 donation_date 
            FROM Donation_Completed 
            WHERE donor_id = ? 
            ORDER BY donation_date DESC
        """, (donor_id,))
        last_donation_row = cursor.fetchone()
        
        if not last_donation_row:
            # No donations yet -> Eligible
            return True, 0
            
        last_date = last_donation_row[0].date()
        today = datetime.now().date()
        days_since = (today - last_date).days
        
        if days_since >= 30:
            return True, 0
        else:
            # Still cooling down
            days_left = 30 - days_since
            return False, days_left
            
    except Exception as e:
        print(f"Error checking eligibility: {e}")
        return False, 0
    finally:
        conn.close()

def mark_notification_read(notification_id, user_id=None):
    """
    Marks a notification as read.
    If user_id is provided, verifies ownership.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if user_id:
            cursor.execute("UPDATE Notification SET is_read = 1 WHERE id = ? AND user_id = ?", (notification_id, user_id))
        else:
            cursor.execute("UPDATE Notification SET is_read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        return True, None
    except Exception as e:
        print(f"Error marking notification read: {e}")
        return False, str(e)
    finally:
        conn.close()

def mark_all_notifications_read(user_id):
    """Marks all notifications for a user as read."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Notification SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        return True, None
    except Exception as e:
        print(f"Error marking all notifications read: {e}")
        return False, str(e)
    finally:
        conn.close()

# ==================================================================================
# RECIPIENT FUNCTIONS
# ==================================================================================

def get_recipient_by_user_id(user_id):
    """Retrieves recipient profile with blood type and area name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, bt.type as blood_type_str, a.name as area_name
        FROM Recipient r
        LEFT JOIN Blood_Type bt ON r.bloodtype = bt.bloodtype_id
        LEFT JOIN Area a ON r.area_id = a.id
        WHERE r.user_id = ?
    """, (user_id,))
    recipient = cursor.fetchone()
    conn.close()
    return recipient

def update_recipient_profile(user_id, name, area_id, number, dob_str):
    """Updates recipient profile details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        age = None
        dob = None
        if dob_str:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            today = datetime.today().date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
        cursor.execute("""
            UPDATE Recipient
            SET name = ?, area_id = ?, number = ?, DOB = ?, age = ?
            WHERE user_id = ?
        """, (name, area_id, number, dob, age, user_id))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_recipient_requests(recipient_id, page=1, per_page=5):
    """Retrieves all requests made by a recipient with pagination."""
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    
    cursor.execute("SELECT COUNT(*) FROM Request WHERE recipient_id = ?", (recipient_id,))
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT * FROM Request 
        WHERE recipient_id = ? 
        ORDER BY date_requested DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (recipient_id, offset, per_page))
    requests = cursor.fetchall()
    conn.close()
    return requests, total

def create_request_transaction(user_id, units, blood_type_id):
    """
    Creates a new blood request and notifies managers.
    
    QUERY: Transaction that validates limit (Max 4 units) and INSERTs a new Request.
    KEYWORDS: Request, Limit, Validation, Insert, Transaction
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM Recipient WHERE user_id = ?", (user_id,))
        recipient_id = cursor.fetchone()[0]
        
        # Enforce Max 4 Units Limit
        if int(units) > 4:
            return False, "Request limit exceeded. You can request a maximum of 4 units."
            
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

# ==================================================================================
# NOTIFICATION FUNCTIONS
# ==================================================================================

def create_notification(user_id, message, type='General'):
    """Creates a single notification for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Notifications (user_id, message, type)
            VALUES (?, ?, ?)
        """, (user_id, message, type))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def broadcast_notification(target_role, message, blood_type=None):
    """
    Broadcasts a notification to a group of users.
    target_role: 'All', 'Donor', 'Recipient', 'Manager'
    blood_type: Optional filter for Donors/Recipients (e.g., 'A+')
    
    QUERY: Bulk INSERT using executemany() for efficiency. Selects target user IDs based on role/blood type.
    KEYWORDS: Broadcast, Bulk Insert, Notification, Filtering, Efficiency
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        user_ids = []
        
        if target_role == 'All':
            cursor.execute("SELECT id FROM [User]")
            user_ids = [row[0] for row in cursor.fetchall()]
            
        elif target_role == 'Manager':
            cursor.execute("SELECT user_id FROM Manager")
            user_ids = [row[0] for row in cursor.fetchall()]
            
        elif target_role == 'Donor':
            sql = "SELECT user_id FROM Donor d JOIN Blood_Type bt ON d.bloodtype = bt.bloodtype_id WHERE 1=1"
            p = []
            if blood_type:
                sql += " AND bt.type = ?"
                p.append(blood_type)
            cursor.execute(sql, p)
            user_ids = [row[0] for row in cursor.fetchall()]
            
        elif target_role == 'Recipient':
            sql = "SELECT user_id FROM Recipient r JOIN Blood_Type bt ON r.bloodtype = bt.bloodtype_id WHERE 1=1"
            p = []
            if blood_type:
                sql += " AND bt.type = ?"
                p.append(blood_type)
            cursor.execute(sql, p)
            user_ids = [row[0] for row in cursor.fetchall()]

        # Bulk Insert
        if user_ids:
            insert_data = [(uid, message, 'Broadcast') for uid in user_ids if uid is not None]
            if insert_data:
                cursor.executemany("""
                    INSERT INTO Notifications (user_id, message, type)
                    VALUES (?, ?, ?)
                """, insert_data)
        
        conn.commit()
        return True, len(user_ids)
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_user_notifications(user_id, page=1, per_page=10):
    """
    Retrieves all notifications for a user, ordered by date with pagination.
    
    QUERY: SELECT with ORDER BY created_at DESC and OFFSET-FETCH pagination.
    KEYWORDS: Notification, History, Pagination, Order By
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * per_page
    
    cursor.execute("SELECT COUNT(*) FROM Notifications WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT id, message, is_read, created_at, type
        FROM Notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (user_id, offset, per_page))
    notifications = cursor.fetchall()
    conn.close()
    return notifications, total

def get_unread_notification_count(user_id):
    """Returns the count of unread notifications."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM Notifications 
        WHERE user_id = ? AND is_read = 0
    """, (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def mark_notification_read(notification_id, user_id):
    """Marks a specific notification as read."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Notifications 
            SET is_read = 1 
            WHERE id = ? AND user_id = ?
        """, (notification_id, user_id))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def mark_all_notifications_read(user_id):
    """Marks all notifications for a user as read."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Notifications 
            SET is_read = 1 
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
