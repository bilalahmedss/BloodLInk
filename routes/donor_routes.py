from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from db import (
    get_donor_by_user_id, get_donor_history, toggle_donor_availability, 
    create_notification, update_donor_profile, get_all_areas, 
    check_donor_eligibility, get_user_notifications, get_unread_notification_count
)
from datetime import datetime, timedelta

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

def is_donor():
    """Checks if the current user has the 'Donor' role."""
    return session.get('role') == 'Donor'

@donor_bp.route('/dashboard')
def dashboard():
    """
    Renders the Donor Dashboard.
    Includes automatic availability check based on 30-day rule.
    Fetches recent notifications.
    """
    if not is_donor(): return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    donor = get_donor_by_user_id(user_id)
    
    if not donor:
        return "Donor profile not found", 404

    # BUSINESS LOGIC: 30-Day Rule Check
    # We check if the donor has donated in the last 30 days.
    # This function returns (True, 0) if eligible, or (False, days_left) if in cooldown.
    # Note: This is a read-only check; it doesn't modify the database.
    is_eligible, days_left = check_donor_eligibility(user_id)
    
    # Refresh donor data after potential auto-update
    donor = get_donor_by_user_id(user_id)
            
    page = request.args.get('page', 1, type=int)
    per_page = 5
    history, total = get_donor_history(donor.id, page, per_page)
    total_pages = (total + per_page - 1) // per_page
    
    # Get Notifications
    notifications, _ = get_user_notifications(user_id, page=1, per_page=5)
    unread_count = get_unread_notification_count(user_id)
    
    return render_template('donor/dashboard.html', donor=donor, history=history, page=page, total_pages=total_pages, 
                           is_eligible=is_eligible, days_left=days_left,
                           notifications=notifications, unread_count=unread_count)

@donor_bp.route('/toggle-availability', methods=['POST'])
def toggle_availability():
    """
    API Endpoint: Toggle donor availability status.
    Enforces 30-day eligibility rule.
    """
    if not is_donor(): return jsonify({'error': 'Unauthorized'}), 403
    
    user_id = session.get('user_id')
    
    # SECURITY CHECK: Server-Side Validation
    # Even though the UI disables the button, we MUST verify eligibility on the server
    # to prevent users from bypassing the UI (e.g., using Postman or DevTools).
    is_eligible, days_left = check_donor_eligibility(user_id)
    if not is_eligible:
        return jsonify({'error': f'Cannot toggle status. You are in cooldown for {days_left} more days.'}), 403
    
    success, result = toggle_donor_availability(user_id)
    
    if success:
        return jsonify({'success': True, 'new_status': result})
    else:
        return jsonify({'error': result}), 500

@donor_bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    """
    Handles donor profile updates.
    POST: Updates profile details.
    GET: Renders edit profile form.
    """
    if not is_donor(): return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        name = request.form['name']
        area_id = request.form['area']
        number = request.form.get('number')
        dob = request.form.get('dob')
        
        success, error = update_donor_profile(user_id, name, area_id, number, dob)
        
        if success:
            return redirect(url_for('donor.dashboard'))
        else:
            return f"Error: {error}", 500
            
    donor = get_donor_by_user_id(user_id)
    areas = get_all_areas()
    return render_template('donor/edit_profile.html', donor=donor, areas=areas)
