from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from db import (
    get_inventory_stats, get_all_donors, get_donor_details_by_id, 
    submit_donation_transaction, get_all_requests, approve_request_transaction, 
    fulfill_request_transaction
)

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

def is_manager():
    return session.get('role') == 'Manager'

@manager_bp.route('/dashboard')
def dashboard():
    if not is_manager(): return redirect(url_for('auth.login'))
    return render_template('manager/dashboard.html', user=session) # Pass session/user info

@manager_bp.route('/donation-entry')
def donation_entry():
    if not is_manager(): return redirect(url_for('auth.login'))
    return render_template('manager/donation_entry.html')

@manager_bp.route('/inventory')
def inventory():
    if not is_manager(): return redirect(url_for('auth.login'))
    
    inventory_data = get_inventory_stats()
    
    return render_template('manager/inventory.html', inventory=inventory_data)

@manager_bp.route('/donors')
def donors():
    if not is_manager(): return redirect(url_for('auth.login'))
    
    donors = get_all_donors()
    
    return render_template('manager/donors_list.html', donors=donors)

@manager_bp.route('/donor-lookup', methods=['POST'])
def donor_lookup():
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    donor_id = request.json.get('donor_id')
    row = get_donor_details_by_id(donor_id)
    
    if row:
        return jsonify({'name': row.name, 'blood_type': row.type})
    else:
        return jsonify({'error': 'Donor not found'}), 404

@manager_bp.route('/submit-donation', methods=['POST'])
def submit_donation():
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    donor_id = data.get('donor_id')
    volume = data.get('volume')
    is_exchange = data.get('is_exchange', False)
    
    success, error = submit_donation_transaction(donor_id, volume, is_exchange)
    
    if success:
        return jsonify({'success': True, 'message': 'Donation recorded successfully'})
    else:
        return jsonify({'error': error}), 500

@manager_bp.route('/requests')
def view_requests():
    if not is_manager(): return redirect(url_for('auth.login'))
    
    requests = get_all_requests()
    
    return render_template('manager/requests.html', requests=requests)

@manager_bp.route('/approve-request/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    manager_user_id = session.get('user_id')
    
    success, error = approve_request_transaction(request_id, manager_user_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 500

@manager_bp.route('/fulfill-request/<int:request_id>', methods=['POST'])
def fulfill_request(request_id):
    if not is_manager(): return jsonify({'error': 'Unauthorized'}), 403
    
    success, error = fulfill_request_transaction(request_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 500
