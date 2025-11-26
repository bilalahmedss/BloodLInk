-- ==========================================================
-- BLOOD DONATION MANAGEMENT SYSTEM - ROBUST SQL SERVER VERSION
-- ==========================================================

CREATE DATABASE BloodLink;
GO

USE BloodLink;
GO

-- ==========================================================
-- USER TABLE
-- ==========================================================
CREATE TABLE [User] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Donor', 'Recipient', 'Manager'))
);
GO

-- ==========================================================
-- BLOOD TYPE TABLE
-- ==========================================================
CREATE TABLE Blood_Type (
    bloodtype_id INT IDENTITY(1,1) PRIMARY KEY,
    type VARCHAR(10) NOT NULL UNIQUE
);
GO

-- ==========================================================
-- DONOR TABLE
-- ==========================================================
CREATE TABLE Donor (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    bloodtype INT NOT NULL,
    status VARCHAR(50),
    area NVARCHAR(255),
    number NVARCHAR(20),
    DOB DATE,
    age INT,
    availability BIT DEFAULT 1,
    user_id INT UNIQUE,
    
    FOREIGN KEY (bloodtype) REFERENCES Blood_Type(bloodtype_id),
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- ==========================================================
-- RECIPIENT TABLE
-- ==========================================================
CREATE TABLE Recipient (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    bloodtype INT NOT NULL,
    area NVARCHAR(255),
    user_id INT UNIQUE,
    
    FOREIGN KEY (bloodtype) REFERENCES Blood_Type(bloodtype_id),
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- ==========================================================
-- MANAGER TABLE
-- ==========================================================
CREATE TABLE Manager (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    user_id INT UNIQUE,
    
    FOREIGN KEY (user_id) REFERENCES [User](id) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

-- ==========================================================
-- REQUEST TABLE
-- ==========================================================
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

-- ==========================================================
-- DONATION_COMPLETED TABLE
-- ==========================================================
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

-- ==========================================================
-- STOCK TABLE
-- ==========================================================
CREATE TABLE Stock (
    bag_id INT IDENTITY(1,1) PRIMARY KEY,
    units INT NOT NULL CHECK (units > 0),
    donation_id INT NOT NULL UNIQUE,
    request_id INT,
    
    FOREIGN KEY (donation_id) REFERENCES Donation_Completed(id) ON DELETE CASCADE,
    FOREIGN KEY (request_id) REFERENCES Request(id) ON DELETE SET NULL
);
GO

-- ==========================================================
-- PENDING DONATION TABLE
-- ==========================================================
CREATE TABLE Pending_Donation (
    id INT IDENTITY(1,1) PRIMARY KEY,
    donor_id INT NOT NULL,
    blood_type INT NOT NULL,
    units INT NOT NULL CHECK (units > 0),
    submitted_date DATETIME NOT NULL DEFAULT GETDATE(),
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    approved_by INT,
    approval_date DATETIME,
    notes NVARCHAR(255),
    
    FOREIGN KEY (donor_id) REFERENCES Donor(id) ON DELETE CASCADE,
    FOREIGN KEY (blood_type) REFERENCES Blood_Type(bloodtype_id),
    FOREIGN KEY (approved_by) REFERENCES Manager(id) ON DELETE SET NULL
);
GO

-- ==========================================================
-- DONOR HISTORY TABLE
-- ==========================================================
CREATE TABLE Donor_History (
    donor_id INT NOT NULL,
    [date] DATETIME NOT NULL,
    unit INT NOT NULL CHECK (unit > 0),
    
    PRIMARY KEY (donor_id, [date]),
    FOREIGN KEY (donor_id) REFERENCES Donor(id) ON DELETE CASCADE
);
GO

-- ==========================================================
-- NOTIFICATIONS TABLE
-- ==========================================================
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
-- INSERT SAMPLE BLOOD TYPES
-- ==========================================================
INSERT INTO Blood_Type (type)
VALUES ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-'), ('O+'), ('O-');
GO