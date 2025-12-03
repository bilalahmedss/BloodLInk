from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_user_by_email_password, get_user_name_by_role_id, register_user_transaction, get_all_areas

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    POST: Authenticates user and sets session variables.
    GET: Renders login page.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email_password(email, password)
        
        if user:
            # SESSION MANAGEMENT:
            # We use Flask's session to store the user's ID and Role.
            # This allows us to protect routes using decorators or checks like `is_manager()`.
            session.permanent = True
            session['user_id'] = user.id
            session['role'] = user.role
            
            # Fetch and store user's name for display
            name = get_user_name_by_role_id(user.role, user.id)
            session['name'] = name if name else 'User'
            
            # Redirect based on role
            if user.role == 'Manager':
                return redirect(url_for('manager.dashboard'))
            elif user.role == 'Donor':
                return redirect(url_for('donor.dashboard'))
            elif user.role == 'Recipient':
                return redirect(url_for('recipient.dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    POST: Creates new user and role-specific profile.
    GET: Renders registration page with area options.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        
        # Collect additional fields for Donor/Recipient
        kwargs = {
            'blood_type': request.form.get('blood_type'),
            'dob': request.form.get('dob'),
            'area_id': request.form.get('area'), # Form sends area_id as 'area'
            'number': request.form.get('number')
        }
        
        # ATOMIC REGISTRATION:
        # We use a transaction to ensure that both the User account and the specific
        # Role profile (Donor/Recipient/Manager) are created together.
        # If one fails, the entire operation is rolled back to prevent data inconsistency.
        success, error = register_user_transaction(email, password, role, name, **kwargs)
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Error: {error}', 'error')

    areas = get_all_areas()
    return render_template('register.html', areas=areas)

@auth_bp.route('/logout')
def logout():
    """Clears session and redirects to login."""
    session.clear()
    return redirect(url_for('auth.login'))
