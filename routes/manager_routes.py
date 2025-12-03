from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from db import (
    get_inventory_stats, get_all_donors, search_donor, 
    submit_donation_transaction, get_all_requests, approve_request_transaction, 
    fulfill_request_transaction, get_active_requests, broadcast_notification,
    get_all_areas
)

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

def is_manager():
    """Checks if the current user has the 'Manager' role."""
    return session.get('role') == 'Manager'

@manager_bp.route('/send-notification', methods=['GET', 'POST'])
def send_notification():
    """
    Handles manual notification broadcasting by a Manager.
    POST: Sends notification to target group.
    GET: Renders notification form.
    """
    if not is_manager(): return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        target_role = request.form.get('target_role')
        blood_type = request.form.get('blood_type')
        message = request.form.get('message')
        
        success, count_or_error = broadcast_notification(target_role, message, blood_type)
        
        if success:
            flash(f'Notification sent to {count_or_error} users.')
            return redirect(url_for('manager.dashboard'))
        else:
            flash(f'Error sending notification: {count_or_error}')
            
    return render_template('manager/send_notification.html')

@manager_bp.route('/dashboard')
def dashboard():
    """Renders the Manager Dashboard."""
    if not is_manager(): return redirect(url_for('auth.login'))
    return render_template('manager/dashboard.html', user=session)

@manager_bp.route('/donation-entry')
def donation_entry():
    """
    Renders the Donation Entry form.
    Fetches active requests to populate the exchange dropdown initially (though JS handles dynamic updates).
    """
    if not is_manager(): return redirect(url_for('auth.login'))
    requests = get_active_requests()
    return render_template('manager/donation_entry.html', requests=requests)

@manager_bp.route('/inventory')
def inventory():
    """
    Displays the current blood inventory.
    Supports filtering by Area and Blood Type via query parameters.
    """
    if not is_manager(): return redirect(url_for('auth.login'))
    
    area_id = request.args.get('area_id')
    blood_type = request.args.get('blood_type')
    
    inventory_data = get_inventory_stats(area_id, blood_type)
    areas = get_all_areas()
    
    return render_template('manager/inventory.html', inventory=inventory_data, areas=areas, 
                           current_area=area_id, current_blood_type=blood_type)

@manager_bp.route('/donors')
def donors():
    """
    Displays a paginated list of all donors.
    Supports filtering by Area and Blood Type.
    """
    if not is_manager(): return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    area_id = request.args.get('area_id')
    blood_type = request.args.get('blood_type')
    
    per_page = 10
    donors, total = get_all_donors(page, per_page, area_id, blood_type)
    
    total_pages = (total + per_page - 1) // per_page
    areas = get_all_areas()
    
    return render_template('manager/donors_list.html', donors=donors, page=page, total_pages=total_pages,
                           areas=areas, current_area=area_id, current_blood_type=blood_type)

@manager_bp.route('/donor-lookup', methods=['POST'])
def donor_lookup():
    """
    API Endpoint: Look up a donor by ID or Name.
    Returns: JSON list of matching donors.
    """
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    query = request.json.get('query')
    if not query: return jsonify({'error': 'No query provided'}), 400
    
    rows = search_donor(query)
    
    results = []
    for row in rows:
        results.append({'id': row.id, 'name': row.name, 'blood_type': row.type, 'area_id': row.area_id})
        
    return jsonify({'results': results})

@manager_bp.route('/get-requests-by-area/<int:area_id>', methods=['GET'])
def get_requests_by_area(area_id):
    """
    API Endpoint: Get active requests filtered by a specific Area ID.
    Used for dynamic dropdown population in Exchange donations.
    """
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    requests = get_active_requests(area_id)
    
    results = []
    for req in requests:
        results.append({
            'id': req.id,
            'name': req.name,
            'type': req.type,
            'units_required': req.units_required,
            'units_collected': req.units_collected
        })
        
    return jsonify({'requests': results})

@manager_bp.route('/submit-donation', methods=['POST'])
def submit_donation():
    """
    API Endpoint: Submit a donation (Voluntary or Exchange).
    Handles transaction logic via db.submit_donation_transaction.
    """
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    donor_id = data.get('donor_id')
    volume = data.get('volume')
    is_exchange = data.get('is_exchange', False)
    request_id = data.get('request_id') # Optional, for exchange
    
    # TRANSACTION WRAPPER:
    # This function handles the complex logic of recording a donation.
    # It updates stock, records history, and if it's an exchange, checks the request status.
    # It also enforces the 30-day rule by resetting the donor's availability.
    success, error = submit_donation_transaction(donor_id, volume, is_exchange, request_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Donation recorded successfully'})
    else:
        return jsonify({'error': error}), 500

@manager_bp.route('/requests')
def view_requests():
    """Displays all blood requests with pagination."""
    if not is_manager(): return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    requests, total = get_all_requests(page, per_page)
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('manager/requests.html', requests=requests, page=page, total_pages=total_pages)

@manager_bp.route('/approve-request/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    """API Endpoint: Approve a pending blood request."""
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    manager_user_id = session.get('user_id')
    # APPROVAL WORKFLOW:
    # 1. Updates request status to 'Approved'.
    # 2. Notifies the Recipient.
    # 3. (Previously) Broadcasted to donors, but now removed to reduce spam.
    success, error = approve_request_transaction(request_id, manager_user_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 500

@manager_bp.route('/fulfill-request/<int:request_id>', methods=['POST'])
def fulfill_request(request_id):
    """API Endpoint: Manually fulfill a request (deducts stock)."""
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    success, error = fulfill_request_transaction(request_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 500
