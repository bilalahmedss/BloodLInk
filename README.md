# BloodLink – Connecting Donors and Recipients 

**BloodLink** is a web-based system designed to streamline the blood donation management process. It supports user registration and authentication for Donors, Recipients, and Managers, along with providing role-based dashboards and database integration.

## Table of Contents:
- [Modules](#modules)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Run it locally](#run-it-locally)
- [Notes](#notes)

## Modules
### 1. Registration & Authentication
- Users can register as **Donor** or **Recipient**.
- The login page is shared for all user types.
- Upon login, the system checks the credentials and redirects users to their respective dashboards based on their role.
- The **Manager** role is hardcoded in the database and not available for user registration.



### 2. Dashboards
- Role-based dashboards that display relevant information and actions for each user type.

### 3. Database Integration
- Uses **SQL Server** for storing user and donation data.
- Handles registration, blood donation requests, and management functions.

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: SQL Server
- **Other**: ODBC Driver for SQL Server

## Installation

### Prerequisites
- **Python 3.11** or higher
- **SQL Server** 


## Steps

1. **Clone the repository**:
    ```bash
    git clone https://github.com/bilalahmedss/BloodLInk
    ```

2. **Navigate to the project directory**:
    ```bash
    cd BloodLInk
    ```
3. **Create a virtual environment (Powershell)**:
   - ```bash
     python -m venv .venv
    - ```bash
      .\.venv\Scripts\Activate.ps1
5. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

6. **Set up SQL Server and create the database**:
    - Run the SQL script in `Database/create.sql` to set up the tables in SQL Server.


## Run it locally

1. **Run the app**:
    ```bash
    python app.py
    ```

2. **Open your browser** and access the following page:
    -  [http://127.0.0.1:5000](http://127.0.0.1:5000)
    

## Notes
- Templates are stored in the `Screens/` folder.

