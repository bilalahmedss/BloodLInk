

# BloodLink 🩸
A web-based blood donation management system built with Python, Flask, and SQL Server.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Notes](#notes)

---

## Overview
BloodLink helps hospitals and organizations manage blood donations, requests, and users. It supports registration and authentication for Donors, Recipients, and Managers, with role-based dashboards and secure data storage.

## Features
- **User Registration:** Donor, Recipient, and Manager roles
- **Secure Login:** Authentication for all user types
- **Role-Based Dashboards:** Personalized views and actions
- **Blood Request Management:** Request and track blood donations
- **Database Integration:** SQL Server backend
- **Modern UI:** Responsive HTML screens with Tailwind CSS
- **Favicon Support:** Custom logo in browser tab

## Tech Stack
- **Frontend:** HTML, CSS (Tailwind), JavaScript
- **Backend:** Python, Flask, pyodbc
- **Database:** SQL Server

## Installation

### Prerequisites
- Python 3.11+
- SQL Server (local or remote)
- Microsoft ODBC Driver for SQL Server (ODBC Driver 17 or 18)

### Steps
1. Clone or download the repository.
2. Create and activate a virtual environment:
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```
3. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```
4. Set up SQL Server and create the database/tables using `Database/create.sql`.
5. (Optional) Set environment variables for custom DB settings:
	```powershell
	$env:MSSQL_SERVER = 'localhost\\SQLEXPRESS'
	$env:MSSQL_DATABASE = 'BloodLink'
	$env:MSSQL_DRIVER = 'ODBC Driver 17 for SQL Server'
	$env:SECRET_KEY = 'your-secret-key'
	```

## Usage
1. Run the app:
	```powershell
	python app.py
	```
2. Open your browser to:
	- Registration: http://127.0.0.1:5000/register
	- Login: http://127.0.0.1:5000/login

## Notes
- HTML templates are in the `Screens/` folder.
- Place your favicon/logo in the `static` folder and reference it in your HTML `<head>`.
- Set a secure `SECRET_KEY` for production.
- For any issues, check your SQL Server connection, template paths, and environment variables.
