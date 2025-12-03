from flask import Flask
import pyodbc

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    # Update with your actual SQL Server connection string
    DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING') or \
        'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=BloodLink;Trusted_Connection=yes;'
    
    from datetime import timedelta
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize DB connection
    # We use raw pyodbc for direct SQL execution as per project requirements.
    
    from routes.auth_routes import auth_bp
    from routes.manager_routes import manager_bp
    from routes.donor_routes import donor_bp
    from routes.recipient_routes import recipient_bp
    from routes.main_routes import main_bp
    from routes.notification_routes import notification_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(recipient_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(notification_bp)

    @app.after_request
    def add_header(response):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response

    return app


