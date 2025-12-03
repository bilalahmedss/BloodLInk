from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from db import (
    get_recipient_by_user_id, get_recipient_requests, create_request_transaction, 
    update_recipient_profile, get_all_areas, get_user_notifications, get_unread_notification_count
)

recipient_bp = Blueprint('recipient', __name__, url_prefix='/recipient')

def is_recipient():
    """Checks if the current user has the 'Recipient' role."""
    return session.get('role') == 'Recipient'

@recipient_bp.route('/dashboard')
def dashboard():
    """
    Renders the Recipient Dashboard.
    Displays profile information and a paginated history of blood requests.
    """
    if not is_recipient(): return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    recipient = get_recipient_by_user_id(user_id)
    
    if not recipient:
        return "Recipient profile not found", 404
        
    page = request.args.get('page', 1, type=int)
    per_page = 5
    requests, total = get_recipient_requests(recipient.id, page, per_page)
    
    total_pages = (total + per_page - 1) // per_page
    
    # Get Notifications
    notifications, _ = get_user_notifications(user_id, page=1, per_page=5)
    unread_count = get_unread_notification_count(user_id)
    
    return render_template('recipient/dashboard.html', recipient=recipient, requests=requests, page=page, total_pages=total_pages,
                           notifications=notifications, unread_count=unread_count)

@recipient_bp.route('/create-request', methods=['POST'])
def create_request():
    """
    Handles submission of a new blood request.
    Creates a request record and notifies managers.
    """
    if not is_recipient(): return jsonify({'error': 'Unauthorized'}), 403
    
    user_id = session.get('user_id')
    units = request.form.get('units')
    blood_type_id = request.form.get('blood_type')
    
    # BUSINESS RULE: Max 4 Units
    # The `create_request_transaction` function enforces a strict limit of 4 units per request.
    # This prevents hoarding and ensures fair distribution of blood stock.
    success, error = create_request_transaction(user_id, units, blood_type_id)
    
    if success:
        flash('Request submitted successfully')
    else:
        flash(f'Error: {error}')
        
    return redirect(url_for('recipient.dashboard'))

@recipient_bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    """
    Handles recipient profile updates.
    POST: Updates profile details.
    GET: Renders edit profile form.
    """
    if not is_recipient(): return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        name = request.form['name']
        area_id = request.form['area']
        number = request.form.get('number')
        dob = request.form.get('dob')
        
        success, error = update_recipient_profile(user_id, name, area_id, number, dob)
        
        if success:
            flash('Profile updated successfully')
            return redirect(url_for('recipient.dashboard'))
        else:
            flash(f'Error: {error}')
            
    recipient = get_recipient_by_user_id(user_id)
    areas = get_all_areas()
    return render_template('recipient/edit_profile.html', recipient=recipient, areas=areas)
