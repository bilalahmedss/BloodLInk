-- ==========================================================
-- BLOOD DONATION MANAGEMENT SYSTEM - COMPREHENSIVE SEED DATA
-- ==========================================================
-- This script assumes the database schema is already created.
-- It populates the database with rich data for testing all features.
-- UPDATED: Uses dynamic ID lookups to prevent Foreign Key errors.

USE BloodLink;
GO

-- ==========================================================
-- 1. CLEANUP EXISTING DATA
-- ==========================================================
DELETE FROM Notifications;
DELETE FROM Stock;
DELETE FROM Donor_History;
DELETE FROM Donation_Completed;
DELETE FROM Request;
DELETE FROM Donor;
DELETE FROM Recipient;
DELETE FROM Manager;
DELETE FROM [User];
DELETE FROM Area;
DELETE FROM Blood_Type;

-- Reseeding identities (good practice, but we won't rely on it for IDs)
DBCC CHECKIDENT ('[User]', RESEED, 0);
DBCC CHECKIDENT ('Blood_Type', RESEED, 0);
DBCC CHECKIDENT ('Area', RESEED, 0);
DBCC CHECKIDENT ('Donor', RESEED, 0);
DBCC CHECKIDENT ('Recipient', RESEED, 0);
DBCC CHECKIDENT ('Manager', RESEED, 0);
DBCC CHECKIDENT ('Request', RESEED, 0);
DBCC CHECKIDENT ('Donation_Completed', RESEED, 0);
DBCC CHECKIDENT ('Stock', RESEED, 0);
DBCC CHECKIDENT ('Notifications', RESEED, 0);
GO

-- ==========================================================
-- 2. REFERENCE DATA
-- ==========================================================

-- Blood Types
INSERT INTO Blood_Type (type) VALUES ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-'), ('O+'), ('O-');

-- Areas
INSERT INTO Area (name) VALUES ('Clifton'), ('Bahria Town'), ('DHA'), ('Johar'), ('Gulshan'), ('PECHS'), ('North Nazimabad'), ('Malir');

-- ==========================================================
-- 3. USERS & PROFILES
-- ==========================================================

-- Manager
INSERT INTO [User] (email, password, role) VALUES ('manager@bloodlink.com', 'admin123', 'Manager');
INSERT INTO Manager (name, user_id) 
VALUES ('System Admin', (SELECT id FROM [User] WHERE email = 'manager@bloodlink.com'));

-- Donors
-- 1. Ali (A+, Clifton)
INSERT INTO [User] (email, password, role) VALUES ('ali@test.com', 'pass123', 'Donor');
INSERT INTO Donor (name, bloodtype, status, area_id, number, DOB, age, availability, user_id) 
VALUES ('Ali Khan', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), 
        'Active', 
        (SELECT id FROM Area WHERE name = 'Clifton'), 
        '0300-1111111', '1990-01-01', 34, 1, 
        (SELECT id FROM [User] WHERE email = 'ali@test.com'));

-- 2. Bilal (B+, DHA)
INSERT INTO [User] (email, password, role) VALUES ('bilal@test.com', 'pass123', 'Donor');
INSERT INTO Donor (name, bloodtype, status, area_id, number, DOB, age, availability, user_id) 
VALUES ('Bilal Sheikh', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B+'), 
        'Active', 
        (SELECT id FROM Area WHERE name = 'DHA'), 
        '0300-2222222', '1992-02-02', 32, 1, 
        (SELECT id FROM [User] WHERE email = 'bilal@test.com'));

-- 3. Sara (O-, Johar)
INSERT INTO [User] (email, password, role) VALUES ('sara@test.com', 'pass123', 'Donor');
INSERT INTO Donor (name, bloodtype, status, area_id, number, DOB, age, availability, user_id) 
VALUES ('Sara Ahmed', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O-'), 
        'Active', 
        (SELECT id FROM Area WHERE name = 'Johar'), 
        '0300-3333333', '1995-03-03', 29, 0, 
        (SELECT id FROM [User] WHERE email = 'sara@test.com'));

-- 4. Zara (AB+, Gulshan)
INSERT INTO [User] (email, password, role) VALUES ('zara@test.com', 'pass123', 'Donor');
INSERT INTO Donor (name, bloodtype, status, area_id, number, DOB, age, availability, user_id) 
VALUES ('Zara Raza', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'AB+'), 
        'Active', 
        (SELECT id FROM Area WHERE name = 'Gulshan'), 
        '0300-4444444', '1998-04-04', 26, 1, 
        (SELECT id FROM [User] WHERE email = 'zara@test.com'));

-- Recipients
-- 1. Fatima (Needs A+, Clifton)
INSERT INTO [User] (email, password, role) VALUES ('fatima@test.com', 'pass123', 'Recipient');
INSERT INTO Recipient (name, bloodtype, area_id, number, DOB, age, user_id) 
VALUES ('Fatima Yusuf', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), 
        (SELECT id FROM Area WHERE name = 'Clifton'), 
        '0300-5555555', '1985-05-05', 39, 
        (SELECT id FROM [User] WHERE email = 'fatima@test.com'));

-- 2. Omar (Needs B+, DHA)
INSERT INTO [User] (email, password, role) VALUES ('omar@test.com', 'pass123', 'Recipient');
INSERT INTO Recipient (name, bloodtype, area_id, number, DOB, age, user_id) 
VALUES ('Omar Farooq', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B+'), 
        (SELECT id FROM Area WHERE name = 'DHA'), 
        '0300-6666666', '1980-06-06', 44, 
        (SELECT id FROM [User] WHERE email = 'omar@test.com'));

-- 3. Usman (Needs O+, Johar)
INSERT INTO [User] (email, password, role) VALUES ('usman@test.com', 'pass123', 'Recipient');
INSERT INTO Recipient (name, bloodtype, area_id, number, DOB, age, user_id) 
VALUES ('Usman Ghani', 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), 
        (SELECT id FROM Area WHERE name = 'Johar'), 
        '0300-7777777', '2000-07-07', 24, 
        (SELECT id FROM [User] WHERE email = 'usman@test.com'));

-- ==========================================================
-- 4. REQUESTS
-- ==========================================================

-- 1. Pending Request: Fatima (Clifton) needs 2 units of A+
INSERT INTO Request (status, recipient_id, units_required, units_collected, blood_type, date_requested) 
VALUES ('Pending', 
        (SELECT id FROM Recipient WHERE name = 'Fatima Yusuf'), 
        2, 0, 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), 
        DATEADD(day, -2, GETDATE()));

-- 2. Approved Request: Omar (DHA) needs 4 units of B+
INSERT INTO Request (status, recipient_id, units_required, units_collected, blood_type, date_requested, approved_by) 
VALUES ('Approved', 
        (SELECT id FROM Recipient WHERE name = 'Omar Farooq'), 
        4, 1, 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B+'), 
        DATEADD(day, -5, GETDATE()), 
        (SELECT id FROM Manager WHERE name = 'System Admin'));

-- 3. Fulfilled Request: Usman (Johar) needed 1 unit of O+
INSERT INTO Request (status, recipient_id, units_required, units_collected, blood_type, date_requested, approved_by, date_fulfilled) 
VALUES ('Fulfilled', 
        (SELECT id FROM Recipient WHERE name = 'Usman Ghani'), 
        1, 1, 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), 
        DATEADD(day, -10, GETDATE()), 
        (SELECT id FROM Manager WHERE name = 'System Admin'), 
        DATEADD(day, -8, GETDATE()));

-- ==========================================================
-- 5. DONATIONS & STOCK (Historical Data)
-- ==========================================================

-- 1. Old Donation by Ali (A+, Clifton) - 60 days ago
INSERT INTO Donation_Completed (units, donor_id, blood_type, donation_date, is_exchange)
VALUES (1, 
        (SELECT id FROM Donor WHERE name = 'Ali Khan'), 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), 
        DATEADD(day, -60, GETDATE()), 0);

INSERT INTO Stock (units, donation_id, area_id)
VALUES (1, SCOPE_IDENTITY(), (SELECT id FROM Area WHERE name = 'Clifton'));

INSERT INTO dbo.Donor_History (donor_id, [date], [unit]) 
VALUES ((SELECT id FROM Donor WHERE name = 'Ali Khan'), DATEADD(day, -60, GETDATE()), 1);


-- 2. Recent Donation by Sara (O-, Johar) - 10 days ago (Fulfilled Usman's request)
INSERT INTO Donation_Completed (request_id, units, donor_id, blood_type, donation_date, is_exchange)
VALUES ((SELECT id FROM Request WHERE recipient_id = (SELECT id FROM Recipient WHERE name = 'Usman Ghani')), 
        1, 
        (SELECT id FROM Donor WHERE name = 'Sara Ahmed'), 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O-'), 
        DATEADD(day, -10, GETDATE()), 1);

INSERT INTO Stock (units, donation_id, request_id, area_id)
VALUES (1, SCOPE_IDENTITY(), 
        (SELECT id FROM Request WHERE recipient_id = (SELECT id FROM Recipient WHERE name = 'Usman Ghani')), 
        (SELECT id FROM Area WHERE name = 'Johar'));

INSERT INTO dbo.Donor_History (donor_id, [date], [unit]) 
VALUES ((SELECT id FROM Donor WHERE name = 'Sara Ahmed'), DATEADD(day, -10, GETDATE()), 1);


-- 3. Donation by Bilal (B+, DHA) - 5 days ago (Partial fulfillment for Omar)
INSERT INTO Donation_Completed (request_id, units, donor_id, blood_type, donation_date, is_exchange)
VALUES ((SELECT id FROM Request WHERE recipient_id = (SELECT id FROM Recipient WHERE name = 'Omar Farooq')), 
        1, 
        (SELECT id FROM Donor WHERE name = 'Bilal Sheikh'), 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B+'), 
        DATEADD(day, -5, GETDATE()), 1);

INSERT INTO Stock (units, donation_id, request_id, area_id)
VALUES (1, SCOPE_IDENTITY(), 
        (SELECT id FROM Request WHERE recipient_id = (SELECT id FROM Recipient WHERE name = 'Omar Farooq')), 
        (SELECT id FROM Area WHERE name = 'DHA'));

INSERT INTO dbo.Donor_History (donor_id, [date], [unit]) 
VALUES ((SELECT id FROM Donor WHERE name = 'Bilal Sheikh'), DATEADD(day, -5, GETDATE()), 1);


-- ==========================================================
-- 6. STOCK SEEDING FOR TESTING
-- ==========================================================

-- Ensure Clifton has enough A+ stock for swap testing
INSERT INTO Donation_Completed (units, donor_id, blood_type, donation_date, is_exchange)
VALUES (4, 
        (SELECT id FROM Donor WHERE name = 'Ali Khan'), 
        (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), 
        DATEADD(day, -90, GETDATE()), 0);

INSERT INTO Stock (units, donation_id, area_id)
VALUES (4, SCOPE_IDENTITY(), (SELECT id FROM Area WHERE name = 'Clifton'));

-- ==========================================================
-- 7. NOTIFICATIONS
-- ==========================================================

INSERT INTO Notifications (user_id, message, is_read, type, created_at) VALUES
((SELECT id FROM [User] WHERE email = 'ali@test.com'), 'Urgent: Blood needed matching your type!', 0, 'Broadcast', GETDATE()),
((SELECT id FROM [User] WHERE email = 'fatima@test.com'), 'Your request has been approved and is in process.', 1, 'General', DATEADD(day, -1, GETDATE())),
((SELECT id FROM [User] WHERE email = 'manager@bloodlink.com'), 'New blood request submitted by Fatima Yusuf.', 0, 'General', DATEADD(day, -2, GETDATE()));

PRINT 'Comprehensive Test Data Populated Successfully.';
