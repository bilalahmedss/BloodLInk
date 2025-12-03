-- ==========================================================
-- BLOOD DONATION MANAGEMENT SYSTEM - FINAL SCHEMA
-- ==========================================================

CREATE DATABASE BloodLink;
GO

USE BloodLink;
GO

-- ==========================================================
-- 1. CORE TABLES
-- ==========================================================

-- User Table: Central authentication
CREATE TABLE [User] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Donor', 'Recipient', 'Manager'))
);
GO

-- Blood Type Table: Lookup for blood types
CREATE TABLE Blood_Type (
    bloodtype_id INT IDENTITY(1,1) PRIMARY KEY,
    type VARCHAR(10) NOT NULL UNIQUE
);
GO

-- Area Table: Lookup for locations
CREATE TABLE Area (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE
);
GO

-- ==========================================================
-- 2. ROLE-SPECIFIC TABLES
-- ==========================================================

-- Donor Table: Extends User
CREATE TABLE Donor (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    bloodtype INT NOT NULL,
    status VARCHAR(50),
    area_id INT,
    number NVARCHAR(20),
    DOB DATE,
    age INT,
    availability BIT DEFAULT 1,
    user_id INT UNIQUE,
    
    FOREIGN KEY (bloodtype) REFERENCES Blood_Type(bloodtype_id),
    FOREIGN KEY (area_id) REFERENCES Area(id),
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- Recipient Table: Extends User
CREATE TABLE Recipient (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    bloodtype INT NOT NULL,
    area_id INT,
    number NVARCHAR(20),
    DOB DATE,
    age INT,
    user_id INT UNIQUE,
    
    FOREIGN KEY (bloodtype) REFERENCES Blood_Type(bloodtype_id),
    FOREIGN KEY (area_id) REFERENCES Area(id),
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- Manager Table: Extends User (Global Role)
CREATE TABLE Manager (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    user_id INT UNIQUE,
    
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- ==========================================================
-- 3. OPERATIONAL TABLES
-- ==========================================================

-- Request Table: Tracks blood requests
CREATE TABLE Request (
    id INT IDENTITY(1,1) PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Fulfilled', 'Rejected')),
    recipient_id INT NOT NULL,
    units_required INT NOT NULL CHECK (units_required > 0),
    units_collected INT DEFAULT 0,
    date_requested DATE DEFAULT GETDATE(),
    date_fulfilled DATE,
    approved_by INT,
    blood_type INT NOT NULL,
    
    FOREIGN KEY (recipient_id) REFERENCES Recipient(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES Manager(id) ON DELETE SET NULL,
    FOREIGN KEY (blood_type) REFERENCES Blood_Type(bloodtype_id)
);
GO

-- Donation_Completed Table: Records successful donations
CREATE TABLE Donation_Completed (
    id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT,
    units INT NOT NULL CHECK (units > 0),
    donor_id INT NOT NULL,
    blood_type INT NOT NULL,
    donation_date DATETIME DEFAULT GETDATE(),
    is_exchange BIT DEFAULT 0,
    
    FOREIGN KEY (request_id) REFERENCES Request(id) ON DELETE SET NULL,
    FOREIGN KEY (donor_id) REFERENCES Donor(id),
    FOREIGN KEY (blood_type) REFERENCES Blood_Type(bloodtype_id)
);
GO

-- Stock Table: Physical inventory
CREATE TABLE Stock (
    bag_id INT IDENTITY(1,1) PRIMARY KEY,
    units INT NOT NULL CHECK (units > 0),
    donation_id INT NOT NULL UNIQUE,
    request_id INT,
    area_id INT,
    
    FOREIGN KEY (donation_id) REFERENCES Donation_Completed(id) ON DELETE CASCADE,
    FOREIGN KEY (request_id) REFERENCES Request(id) ON DELETE SET NULL,
    FOREIGN KEY (area_id) REFERENCES Area(id)
);
GO

-- Donor History Table: Historical record
CREATE TABLE Donor_History (
    donor_id INT NOT NULL,
    [date] DATETIME NOT NULL,
    unit INT NOT NULL CHECK (unit > 0),
    
    PRIMARY KEY (donor_id, [date]),
    FOREIGN KEY (donor_id) REFERENCES Donor(id) ON DELETE CASCADE
);
GO

-- Notifications Table: System alerts
CREATE TABLE Notifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    is_read BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    type VARCHAR(50) CHECK (type IN ('Broadcast', 'Collection', 'General')),
    
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE CASCADE
);
GO

-- ==========================================================
-- 4. SEED DATA
-- ==========================================================

INSERT INTO Blood_Type (type)
VALUES ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-'), ('O+'), ('O-');
GO

INSERT INTO Area (name)
VALUES ('Clifton'), ('Bahria Town'), ('DHA'), ('Johar'), ('Gulshan'), ('PECHS');
GO