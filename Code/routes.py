# routes.py
"""
Flask routes and business logic for BloodLink app.
Imports database helpers from db.py.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import check_db_connectivity, get_user_by_email, get_user_by_id, insert_donor, insert_recipient

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    ok, err = check_db_connectivity()
    if not ok:
        return f"<h2>Database connection failed</h2><p>{err}</p>", 500
    return render_template('1.0 Welcome.html')

@routes.route('/register')
def register_usertype():
    return render_template('1.1 Usertype.html')

@routes.route('/register/donor', methods=['GET', 'POST'])
def register_donor():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        area = request.form.get('area')
        blood_type = request.form.get('blood_type')
        last_donation = request.form.get('last_donation')
        contact_details = request.form.get('contact_details')
        if not (name and email and password and blood_type):
            flash('Please fill all required donor fields.')
            return render_template('1.2 Donor.html')
        success, msg = insert_donor(name, email, password, area, blood_type, last_donation, contact_details)
        if not success:
            flash(msg)
            return render_template('1.2 Donor.html')
        flash('Donor registration successful. Please login.')
        return redirect(url_for('routes.login'))
    return render_template('1.2 Donor.html')

@routes.route('/register/recipient', methods=['GET', 'POST'])
def register_recipient():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        area = request.form.get('area')
        contact = request.form.get('contact')
        if not (name and email and password and area and contact):
            flash('Please fill all required recipient fields.')
            return render_template('1.3 Recipient.html')
        success, msg = insert_recipient(name, email, password, area, contact)
        if not success:
            flash(msg)
            return render_template('1.3 Recipient.html')
        flash('Recipient registration successful. Please login.')
        return redirect(url_for('routes.login'))
    return render_template('1.3 Recipient.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = get_user_by_email(email)
        if not user or user['password'] != password:
            flash('Invalid email or password. Please try again.')
            return render_template('2.0 Login.html')
        session.clear()
        session['user_id'] = user['id']
        session['role'] = user['role']
        if user['role'] == 'donor':
            return redirect(url_for('routes.donor_dashboard'))
        elif user['role'] == 'recipient':
            return redirect(url_for('routes.recipient_dashboard'))
        elif user['role'] == 'manager':
            return redirect(url_for('routes.manager_dashboard'))
        else:
            flash('Unknown user role. Please contact admin.')
            return render_template('2.0 Login.html')
    return render_template('2.0 Login.html')

@routes.route('/logout')
def logout():
    session.clear()
    flash('Logged out')
    return redirect(url_for('routes.login'))


def get_user_by_session():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or not role:
        return None
    return get_user_by_id(user_id, role)

@routes.route('/dashboard/donor')
def donor_dashboard():
    if session.get('role') != 'donor':
        flash('Access denied')
        return redirect(url_for('routes.login'))
    user = get_user_by_session()
    return render_template('2.1 Donor Dashboard.html', user=user)

@routes.route('/dashboard/recipient')
def recipient_dashboard():
    if session.get('role') != 'recipient':
        flash('Access denied')
        return redirect(url_for('routes.login'))
    user = get_user_by_session()
    return render_template('2.2 Recipient Dashboard.html', user=user)

@routes.route('/dashboard/manager')
def manager_dashboard():
    if session.get('role') != 'manager':
        flash('Access denied')
        return redirect(url_for('routes.login'))
    user = get_user_by_session()
    return render_template('2.3 Manager Dashboard.html', user=user)
