
# BloodLink

## About
BloodLink is a web-based system for blood donation management. It supports registration and authentication for Donors, Recipients, and Managers, and provides dashboards for each role.

## Modules

**1. Registration & Authentication**
- Users can register as Donor, Recipient, or Manager.
- Secure login for all roles.

**2. Dashboards**
- Role-based dashboards show relevant information and actions for each user type.

**3. Database Integration**
- Uses SQL Server for storing user and donation data.

## How to Run

1. Install Python 3.11 and required libraries:
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	```

2. Set up SQL Server and create the database/tables using `Database/create.sql`.

3. (Optional) Set environment variables for custom DB settings:
	```powershell
	$env:MSSQL_SERVER = 'localhost\\SQLEXPRESS'
	$env:MSSQL_DATABASE = 'BloodLink'
	$env:MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
	$env:SECRET_KEY = 'your-secret-key'
	```

4. Run the app:
	```powershell
	python app.py
	```

5. Open your browser to:
	- Registration: http://127.0.0.1:5000/register
	- Login: http://127.0.0.1:5000/login

## Notes
- Templates are in the `Screens/` folder.
- Place your favicon/logo in the `static` folder and reference it in your HTML.
- Set a secure `SECRET_KEY` for production.
