from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from db import get_recipient_by_user_id, get_recipient_requests, create_request_transaction

recipient_bp = Blueprint('recipient', __name__, url_prefix='/recipient')

def is_recipient():
    return session.get('role') == 'Recipient'

@recipient_bp.route('/dashboard')
def dashboard():
    if not is_recipient(): return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    
    recipient = get_recipient_by_user_id(user_id)
    
    if not recipient:
        return "Recipient profile not found", 404
        
    requests = get_recipient_requests(recipient.id)
    
    return render_template('recipient/dashboard.html', recipient=recipient, requests=requests)

@recipient_bp.route('/create-request', methods=['POST'])
def create_request():
    if not is_recipient(): return jsonify({'error': 'Unauthorized'}), 403
    
    user_id = session.get('user_id')
    units = request.form.get('units')
    blood_type_id = request.form.get('blood_type') # Assuming they select from a dropdown
    
    success, error = create_request_transaction(user_id, units, blood_type_id)
    
    if success:
        flash('Request submitted successfully')
    else:
        flash(f'Error: {error}')
        
    return redirect(url_for('recipient.dashboard'))
