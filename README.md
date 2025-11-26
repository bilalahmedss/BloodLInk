# BloodLink 🩸
A web-based blood donation management system built with Python, Flask, and SQL Server.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)

---

## Overview
The project titled **BloodLink** is a web-based application designed to manage blood donation and request processes efficiently. It provides a platform for donors, recipients, and a blood bank manager to interact with a centralized database, ensuring that critical information about blood availability is organized, accurate, and easy to access.

### Purpose and Functionality
The purpose of BloodLink is to simplify and streamline how blood donations and requests are managed.
- **Donors** can register, track their donation history, and mark their availability.
- **Recipients** can create requests for specific blood types and units.
- The **Manager** oversees the entire system by maintaining the blood inventory, validating donations, and monitoring the fulfillment process.

### Scope
BloodLink supports three main user roles:
- **Donors**: Individuals who register their profiles, provide details such as blood type and last donation date, and become available for matching with recipients.
- **Recipients**: Patients or their attendants who can request blood of a certain type based on their area.
- **Manager**: The blood bank authority responsible for maintaining inventory records, monitoring donations, approving or closing requests, and generating reports.

## Features
- **User Registration:** Donor, Recipient, and Manager roles with role-specific profiles (including DOB and Age calculation for Donors).
- **Authentication:** Secure login and session management.
- **Role-Based Dashboards:** Personalized views and actions for each user type.
- **Blood Request Management:** Request, track, and fulfill blood donations.
- **Donation History:** Donor history tracking.
- **Inventory Management:** Real-time blood stock tracking by blood type.
- **Modern UI:** Responsive HTML screens with Tailwind CSS.
- **Blueprint Architecture:** Modular Flask routing.

## Tech Stack
- **Frontend:** HTML, CSS (Tailwind), JavaScript
- **Backend:** Python, Flask, pyodbc
- **Database:** SQL Server

## Project Structure
The project follows a modular Flask application structure with Blueprint-based routing:

```
Main/
│
├── static/               # Static assets (CSS, JS)
│
├── templates/            # HTML Templates
│   ├── donor/            # Donor specific templates
│   ├── manager/          # Manager specific templates
│   ├── recipient/        # Recipient specific templates
│   ├── base.html         # Base layout
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   └── welcome.html      # Landing page
│
├── routes/               # Flask Blueprints
│   ├── auth_routes.py    # Authentication logic
│   ├── donor_routes.py   # Donor logic
│   ├── manager_routes.py # Manager logic
│   ├── recipient_routes.py # Recipient logic
│   └── main_routes.py    # Main/Index logic
│
├── Database/
│   └── create.sql        # Database schema
│
├── app.py                # App factory & Config
├── run.py                # Entry point
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

## Installation

### Prerequisites
- Python 3.8+
- Microsoft SQL Server 2019+ (local or remote)
- Microsoft ODBC Driver for SQL Server (ODBC Driver 17 or 18)
- pip (Python package manager)

### Steps
1. Clone or download the repository.
2. Create and activate a virtual environment:
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
3. Install dependencies:
    ```powershell
    pip install -r requirements.txt
    ```
4. Set up SQL Server and create the BloodLink database:
    - Open SQL Server Management Studio
    - Execute `Database/create.sql` to create tables and schema
    - Update the connection string in `app/config.py` if necessary.

## Usage
1. Activate virtual environment:
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
2. Run the app from the project root directory:
    ```powershell
    python run.py
    ```
3. Open your browser to:
    - **Welcome Page:** http://127.0.0.1:5000/

### User Workflows
- **Donor:** Register → Login → Dashboard → View History → Toggle Availability
- **Recipient:** Register → Login → Dashboard → Create Request → Track Status
- **Manager:** Login → Dashboard → Approve Requests → Fulfill Donations → Manage Inventory → View Donors
