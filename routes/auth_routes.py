from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_user_by_email_password, get_user_name_by_role_id, register_user_transaction

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email_password(email, password)
        
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            
            name = get_user_name_by_role_id(user.role, user.id)
            session['name'] = name if name else 'User'
            
            if user.role == 'Manager':
                return redirect(url_for('manager.dashboard'))
            elif user.role == 'Donor':
                return redirect(url_for('donor.dashboard'))
            elif user.role == 'Recipient':
                return redirect(url_for('recipient.dashboard'))
        else:
            flash('Invalid email or password')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        
        # Collect additional fields
        kwargs = {
            'blood_type': request.form.get('blood_type'),
            'dob': request.form.get('dob'),
            'area': request.form.get('area'),
            'number': request.form.get('number')
        }
        
        success, error = register_user_transaction(email, password, role, name, **kwargs)
        
        if success:
            flash('Registration successful! Please login.')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Error: {error}')

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
