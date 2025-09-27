-- Create BloodLink Database
CREATE DATABASE BloodLink;
GO

USE BloodLink;
GO

-- 1. BLOOD_TYPE Reference Table
CREATE TABLE BLOOD_TYPE (
    BloodTypeID INT PRIMARY KEY IDENTITY(1,1),
    Type VARCHAR(5) UNIQUE NOT NULL
);
GO

-- 2. DONOR Table (User Profile)
CREATE TABLE DONOR (
    DonorID INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    FK_BloodTypeID INT FOREIGN KEY REFERENCES BLOOD_TYPE(BloodTypeID),
    LastDonationDate DATE NOT NULL,
    Area VARCHAR(50) NOT NULL,
    AvailabilityStatus BIT NOT NULL,
    IsEligible BIT NOT NULL
);
GO

-- 3. RECIPIENT Table (User Profile)
CREATE TABLE RECIPIENT (
    RecipientID INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Area VARCHAR(50) NOT NULL,
    ContactDetails VARCHAR(200) NOT NULL
);
GO

-- 4. MANAGER Table (Admin User Profile)
CREATE TABLE MANAGER (
    ManagerID INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL
);
GO

-- 5. BLOOD_REQUEST Table (Recipient Requests)
CREATE TABLE BLOOD_REQUEST (
    RequestID INT PRIMARY KEY IDENTITY(1,1),
    FK_RecipientID INT FOREIGN KEY REFERENCES RECIPIENT(RecipientID),
    FK_BloodTypeID INT FOREIGN KEY REFERENCES BLOOD_TYPE(BloodTypeID),
    UnitsRequired INT NOT NULL,
    RequestLocation VARCHAR(50) NOT NULL,
    RequestDate DATETIME NOT NULL,
    Status VARCHAR(15) NOT NULL CHECK (Status IN ('Open', 'Matched', 'Fulfilled', 'Closed')),
    CancellationDate DATETIME
);
GO

-- 6. DONATION_INTENT Table (Donor Donation Intent)
CREATE TABLE DONATION_INTENT (
    IntentID INT PRIMARY KEY IDENTITY(1,1),
    FK_DonorID INT FOREIGN KEY REFERENCES DONOR(DonorID),
    FK_BloodTypeID INT FOREIGN KEY REFERENCES BLOOD_TYPE(BloodTypeID),
    SubmittedUnits INT NOT NULL,
    SubmissionDate DATETIME NOT NULL,
    Status VARCHAR(15) NOT NULL CHECK (Status IN ('Pending', 'Approved', 'Rejected')),
    FK_ManagerID_Approval INT FOREIGN KEY REFERENCES MANAGER(ManagerID),
    ApprovalDate DATETIME
);
GO

-- 7. INVENTORY Table (Blood Stock)
CREATE TABLE INVENTORY (
    InventoryPK INT PRIMARY KEY IDENTITY(1,1),
    FK_BloodTypeID INT FOREIGN KEY REFERENCES BLOOD_TYPE(BloodTypeID),
    StorageArea VARCHAR(50) NOT NULL,
    TotalUnitsAvailable INT NOT NULL,
    LastUpdatedDate DATETIME NOT NULL
);
GO

-- 8. FULFILLMENT_LOG Table (Manager Actions on Blood Requests)
CREATE TABLE FULFILLMENT_LOG (
    FulfillmentID INT PRIMARY KEY IDENTITY(1,1),
    FK_RequestID INT FOREIGN KEY REFERENCES BLOOD_REQUEST(RequestID),
    FK_ManagerID INT FOREIGN KEY REFERENCES MANAGER(ManagerID),
    FulfillmentDate DATETIME NOT NULL,
    UnitsDelivered INT NOT NULL,
    SourceReferenceID INT NOT NULL
);
GO

-- Delete existing records in BLOOD_TYPE, DONOR, RECIPIENT, and MANAGER tables
DELETE FROM BLOOD_TYPE;
DELETE FROM DONOR;
DELETE FROM RECIPIENT;
DELETE FROM MANAGER;
GO

-- Insert some Blood Types (ensure no duplicates)
INSERT INTO BLOOD_TYPE (Type) 
VALUES ('O+'), ('A+'), ('B+'), ('AB+'), ('O-'), ('A-'), ('B-'), ('AB-');
GO

-- Insert Sample Managers with unique email addresses
INSERT INTO MANAGER (Name, Email, PasswordHash) 
VALUES ('John Doe', 'johndoe1@example.com', 'hashedpassword123'),
       ('Jane Smith', 'janesmith@example.com', 'hashedpassword456');
GO

-- Insert Sample Donors with unique email addresses
INSERT INTO DONOR (Name, Email, PasswordHash, FK_BloodTypeID, LastDonationDate, Area, AvailabilityStatus, IsEligible) 
VALUES ('Alice Johnson', 'alicejohnson@example.com', 'hashedpassword789', 1, '2023-01-01', 'Karachi', 1, 1),
       ('Bob Brown', 'bobbrown@example.com', 'hashedpassword321', 2, '2022-05-15', 'Lahore', 0, 0);
GO

-- Insert Sample Recipients with unique email addresses
INSERT INTO RECIPIENT (Name, Email, PasswordHash, Area, ContactDetails) 
VALUES ('Charlie White', 'charliewhite@example.com', 'hashedpassword654', 'Islamabad', '123-456-7890'),
       ('Diana Green', 'dianagreen@example.com', 'hashedpassword987', 'Peshawar', '987-654-3210');
GO

-- Insert Sample Blood Requests
INSERT INTO BLOOD_REQUEST (FK_RecipientID, FK_BloodTypeID, UnitsRequired, RequestLocation, RequestDate, Status) 
VALUES (1, 1, 2, 'Islamabad', GETDATE(), 'Open'),
       (2, 3, 3, 'Lahore', GETDATE(), 'Open');
GO

-- Insert Sample Donation Intent
INSERT INTO DONATION_INTENT (FK_DonorID, FK_BloodTypeID, SubmittedUnits, SubmissionDate, Status, FK_ManagerID_Approval) 
VALUES (1, 1, 2, GETDATE(), 'Pending', 1),
       (2, 2, 3, GETDATE(), 'Approved', 2);
GO

-- Insert Sample Inventory
INSERT INTO INVENTORY (FK_BloodTypeID, StorageArea, TotalUnitsAvailable, LastUpdatedDate) 
VALUES (1, 'Storage A', 10, GETDATE()),
       (2, 'Storage B', 5, GETDATE());
GO

-- Insert Sample Fulfillment Log
INSERT INTO FULFILLMENT_LOG (FK_RequestID, FK_ManagerID, FulfillmentDate, UnitsDelivered, SourceReferenceID) 
VALUES (1, 1, GETDATE(), 2, 1),
       (2, 2, GETDATE(), 3, 2);
GO

-- Check if everything is inserted correctly
SELECT * FROM BLOOD_TYPE;
SELECT * FROM DONOR;
SELECT * FROM RECIPIENT;
SELECT * FROM MANAGER;
SELECT * FROM BLOOD_REQUEST;
SELECT * FROM DONATION_INTENT;
SELECT * FROM INVENTORY;
SELECT * FROM FULFILLMENT_LOG;
