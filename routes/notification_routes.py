from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from db import get_user_notifications, mark_notification_read, mark_all_notifications_read, get_unread_notification_count

notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notification_bp.route('/')
def view_notifications():
    """
    Renders the user's notification center.
    Displays a paginated list of notifications.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    notifications, total = get_user_notifications(user_id, page, per_page)
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('notifications.html', notifications=notifications, page=page, total_pages=total_pages)

@notification_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
def mark_read(notification_id):
    """
    API Endpoint: Mark a single notification as read.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    success, error = mark_notification_read(notification_id, user_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 500

@notification_bp.route('/mark-all-read', methods=['POST'])
def mark_all_read():
    """
    API Endpoint: Mark all notifications for the current user as read.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    success, error = mark_all_notifications_read(user_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': error}), 500

@notification_bp.route('/unread-count')
def unread_count():
    """
    API Endpoint: Get the count of unread notifications.
    Used for updating the notification badge in the UI.
    """
    if 'user_id' not in session:
        return jsonify({'count': 0})
        
    count = get_unread_notification_count(session['user_id'])
    return jsonify({'count': count})
