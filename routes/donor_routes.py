from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from db import get_donor_by_user_id, get_donor_history, toggle_donor_availability

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

def is_donor():
    return session.get('role') == 'Donor'

@donor_bp.route('/dashboard')
def dashboard():
    if not is_donor(): return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    donor = get_donor_by_user_id(user_id)
    
    if not donor:
        return "Donor profile not found", 404

    history = get_donor_history(donor.id)
    
    return render_template('donor/dashboard.html', donor=donor, history=history)

@donor_bp.route('/toggle-availability', methods=['POST'])
def toggle_availability():
    if not is_donor(): return jsonify({'error': 'Unauthorized'}), 403
    
    user_id = session.get('user_id')
    
    success, result = toggle_donor_availability(user_id)
    
    if success:
        return jsonify({'success': True, 'new_status': result})
    else:
        return jsonify({'error': result}), 500
