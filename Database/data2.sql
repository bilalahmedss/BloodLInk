-- ==========================================================
-- BLOODLINK DEMO DATA (data2.sql) - EXPANDED & ROBUST
-- Rich dataset for Viva Presentation: Inventory, Filters, Location Logic
-- ==========================================================

USE BloodLink;
GO

-- ==========================================================
-- 1. CLEANUP
-- ==========================================================
PRINT 'Cleaning up old demo data...';

DECLARE @DemoEmails TABLE (email NVARCHAR(255));
INSERT INTO @DemoEmails VALUES 
('admin@bloodlink.com'), 
('ali@donor.com'), 
('sara@donor.com'), 
('bilal@donor.com'), 
('zain@donor.com'), 
('fatima@recipient.com'), 
('omer@recipient.com'),
-- New Users
('ahmed@donor.com'), ('zara@donor.com'), ('vikram@donor.com'), ('david@donor.com'), ('hina@donor.com'),
('kamran@recipient.com'), ('sana@recipient.com');

DECLARE @UserIDs TABLE (id INT);
INSERT INTO @UserIDs SELECT id FROM [User] WHERE email IN (SELECT email FROM @DemoEmails);

DELETE FROM Donation_Completed WHERE donor_id IN (SELECT id FROM Donor WHERE user_id IN (SELECT id FROM @UserIDs));
DELETE FROM Request WHERE recipient_id IN (SELECT id FROM Recipient WHERE user_id IN (SELECT id FROM @UserIDs));
DELETE FROM Donor WHERE user_id IN (SELECT id FROM @UserIDs);
DELETE FROM Recipient WHERE user_id IN (SELECT id FROM @UserIDs);
DELETE FROM Manager WHERE user_id IN (SELECT id FROM @UserIDs);
DELETE FROM [User] WHERE id IN (SELECT id FROM @UserIDs);

PRINT 'Cleanup complete.';
GO

-- ==========================================================
-- 1.1 REFERENCE DATA (Blood Types)
-- ==========================================================
PRINT 'Checking Blood Types...';
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'A+') INSERT INTO Blood_Type (type) VALUES ('A+');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'A-') INSERT INTO Blood_Type (type) VALUES ('A-');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'B+') INSERT INTO Blood_Type (type) VALUES ('B+');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'B-') INSERT INTO Blood_Type (type) VALUES ('B-');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'AB+') INSERT INTO Blood_Type (type) VALUES ('AB+');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'AB-') INSERT INTO Blood_Type (type) VALUES ('AB-');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'O+') INSERT INTO Blood_Type (type) VALUES ('O+');
IF NOT EXISTS (SELECT 1 FROM Blood_Type WHERE type = 'O-') INSERT INTO Blood_Type (type) VALUES ('O-');
GO

-- ==========================================================
-- 2. AREAS
-- ==========================================================
PRINT 'Inserting Areas...';

IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'North Nazimabad') INSERT INTO Area (name) VALUES ('North Nazimabad');
IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'Gulshan-e-Iqbal') INSERT INTO Area (name) VALUES ('Gulshan-e-Iqbal');
IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'Federal B Area') INSERT INTO Area (name) VALUES ('Federal B Area');
IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'Malir Cantt') INSERT INTO Area (name) VALUES ('Malir Cantt');
-- Ensure Areas used in lookups exist
IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'Clifton') INSERT INTO Area (name) VALUES ('Clifton');
IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'DHA') INSERT INTO Area (name) VALUES ('DHA');
IF NOT EXISTS (SELECT 1 FROM Area WHERE name = 'Gulshan') INSERT INTO Area (name) VALUES ('Gulshan');
GO

-- ==========================================================
-- 3. USERS & PROFILES
-- ==========================================================
PRINT 'Inserting Users...';

DECLARE @UserId INT;
DECLARE @DonorId INT;
DECLARE @RecipientId INT;
DECLARE @ManagerId INT;
DECLARE @AreaId INT;
DECLARE @DonationId INT;

-- MANAGER
INSERT INTO [User] (email, password, role) VALUES ('admin@bloodlink.com', 'admin123', 'Manager');
SET @UserId = SCOPE_IDENTITY();
INSERT INTO Manager (name, user_id) VALUES ('System Administrator', @UserId);
SET @ManagerId = SCOPE_IDENTITY();

-- ==========================================================
-- DONORS (Diverse Mix)
-- ==========================================================

-- 1. Ali Khan (A+, Clifton, Available)
INSERT INTO [User] (email, password, role) VALUES ('ali@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Clifton';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Ali Khan', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), @AreaId, '03001234567', '1995-05-15', 29, 1);
SET @DonorId = SCOPE_IDENTITY();
-- History & Stock
INSERT INTO Donation_Completed (donor_id, units, blood_type, donation_date, is_exchange) VALUES (@DonorId, 1, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), DATEADD(day, -60, GETDATE()), 0);
SET @DonationId = SCOPE_IDENTITY();
INSERT INTO Donor_History (donor_id, [date], [unit]) VALUES (@DonorId, DATEADD(day, -60, GETDATE()), 1);
INSERT INTO Stock (units, donation_id, area_id) VALUES (1, @DonationId, @AreaId);

-- 2. Sara Ahmed (O-, Gulshan, Available)
INSERT INTO [User] (email, password, role) VALUES ('sara@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Gulshan';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Sara Ahmed', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O-'), @AreaId, '03339876543', '1998-08-20', 26, 1);
SET @DonorId = SCOPE_IDENTITY();
-- History & Stock
INSERT INTO Donation_Completed (donor_id, units, blood_type, donation_date, is_exchange) VALUES (@DonorId, 1, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O-'), DATEADD(day, -40, GETDATE()), 0);
SET @DonationId = SCOPE_IDENTITY();
INSERT INTO Donor_History (donor_id, [date], [unit]) VALUES (@DonorId, DATEADD(day, -40, GETDATE()), 1);
INSERT INTO Stock (units, donation_id, area_id) VALUES (1, @DonationId, @AreaId);

-- 3. Bilal Raza (B+, DHA, Cooldown)
INSERT INTO [User] (email, password, role) VALUES ('bilal@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'DHA';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Bilal Raza', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B+'), @AreaId, '03214567890', '1990-12-10', 34, 0);
SET @DonorId = SCOPE_IDENTITY();
-- History ONLY (No Stock - consumed or just history)
INSERT INTO Donation_Completed (donor_id, units, blood_type, donation_date, is_exchange) VALUES (@DonorId, 1, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B+'), DATEADD(day, -20, GETDATE()), 0);
INSERT INTO Donor_History (donor_id, [date], [unit]) VALUES (@DonorId, DATEADD(day, -20, GETDATE()), 1);

-- 4. Zain Malik (AB-, North Nazimabad, Available)
INSERT INTO [User] (email, password, role) VALUES ('zain@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'North Nazimabad';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Zain Malik', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'AB-'), @AreaId, '03456789012', '2000-01-01', 24, 1);

-- 5. Ahmed Ali (O+, Clifton, Available) - Adds depth to Clifton
INSERT INTO [User] (email, password, role) VALUES ('ahmed@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Clifton';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Ahmed Ali', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), @AreaId, '03005556677', '1993-04-05', 31, 1);
SET @DonorId = SCOPE_IDENTITY();
-- Stock
INSERT INTO Donation_Completed (donor_id, units, blood_type, donation_date, is_exchange) VALUES (@DonorId, 1, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), DATEADD(day, -90, GETDATE()), 0);
SET @DonationId = SCOPE_IDENTITY();
INSERT INTO Donor_History (donor_id, [date], [unit]) VALUES (@DonorId, DATEADD(day, -90, GETDATE()), 1);
INSERT INTO Stock (units, donation_id, area_id) VALUES (1, @DonationId, @AreaId);

-- 6. Zara Khan (A-, Gulshan, Available)
INSERT INTO [User] (email, password, role) VALUES ('zara@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Gulshan';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Zara Khan', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A-'), @AreaId, '03218889900', '1996-11-30', 28, 1);
SET @DonorId = SCOPE_IDENTITY();
-- Stock
INSERT INTO Donation_Completed (donor_id, units, blood_type, donation_date, is_exchange) VALUES (@DonorId, 1, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A-'), DATEADD(day, -100, GETDATE()), 0);
SET @DonationId = SCOPE_IDENTITY();
INSERT INTO Donor_History (donor_id, [date], [unit]) VALUES (@DonorId, DATEADD(day, -100, GETDATE()), 1);
INSERT INTO Stock (units, donation_id, area_id) VALUES (1, @DonationId, @AreaId);

-- 7. Vikram Das (B-, Malir Cantt, Available)
INSERT INTO [User] (email, password, role) VALUES ('vikram@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Malir Cantt';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Vikram Das', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B-'), @AreaId, '03451122334', '1988-02-14', 36, 1);

-- 8. David Masih (AB+, Federal B Area, Available)
INSERT INTO [User] (email, password, role) VALUES ('david@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Federal B Area';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('David Masih', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'AB+'), @AreaId, '03009988776', '1991-09-09', 33, 1);

-- 9. Hina Shah (O+, DHA, Available)
INSERT INTO [User] (email, password, role) VALUES ('hina@donor.com', '123456', 'Donor');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'DHA';
INSERT INTO Donor (name, user_id, bloodtype, area_id, number, DOB, age, availability) 
VALUES ('Hina Shah', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), @AreaId, '03337776655', '1999-06-25', 25, 1);
SET @DonorId = SCOPE_IDENTITY();
-- Stock
INSERT INTO Donation_Completed (donor_id, units, blood_type, donation_date, is_exchange) VALUES (@DonorId, 1, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), DATEADD(day, -45, GETDATE()), 0);
SET @DonationId = SCOPE_IDENTITY();
INSERT INTO Donor_History (donor_id, [date], [unit]) VALUES (@DonorId, DATEADD(day, -45, GETDATE()), 1);
INSERT INTO Stock (units, donation_id, area_id) VALUES (1, @DonationId, @AreaId);


-- ==========================================================
-- RECIPIENTS & REQUESTS
-- ==========================================================

-- 1. Fatima Noor (Needs A+ in Clifton)
INSERT INTO [User] (email, password, role) VALUES ('fatima@recipient.com', '123456', 'Recipient');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Clifton';
INSERT INTO Recipient (name, user_id, bloodtype, area_id, number, DOB, age) 
VALUES ('Fatima Noor', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), @AreaId, '03001112233', '1985-03-10', 39);
SET @RecipientId = SCOPE_IDENTITY();
-- Pending Request
INSERT INTO Request (recipient_id, units_required, units_collected, status, blood_type, date_requested)
VALUES (@RecipientId, 2, 0, 'Pending', (SELECT bloodtype_id FROM Blood_Type WHERE type = 'A+'), GETDATE());

-- 2. Omer Sheikh (Needs O+ in Gulshan)
INSERT INTO [User] (email, password, role) VALUES ('omer@recipient.com', '123456', 'Recipient');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Gulshan';
INSERT INTO Recipient (name, user_id, bloodtype, area_id, number, DOB, age) 
VALUES ('Omer Sheikh', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), @AreaId, '03334445566', '1992-07-22', 32);
SET @RecipientId = SCOPE_IDENTITY();
-- Approved Request (Partially collected)
INSERT INTO Request (recipient_id, units_required, units_collected, status, blood_type, date_requested, approved_by)
VALUES (@RecipientId, 3, 1, 'Approved', (SELECT bloodtype_id FROM Blood_Type WHERE type = 'O+'), DATEADD(hour, -5, GETDATE()), @ManagerId);

-- 3. Kamran Khan (Needs B- in Malir Cantt)
INSERT INTO [User] (email, password, role) VALUES ('kamran@recipient.com', '123456', 'Recipient');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Malir Cantt';
INSERT INTO Recipient (name, user_id, bloodtype, area_id, number, DOB, age) 
VALUES ('Kamran Khan', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B-'), @AreaId, '03215554433', '1980-01-20', 44);
SET @RecipientId = SCOPE_IDENTITY();
-- Pending Request
INSERT INTO Request (recipient_id, units_required, units_collected, status, blood_type, date_requested)
VALUES (@RecipientId, 1, 0, 'Pending', (SELECT bloodtype_id FROM Blood_Type WHERE type = 'B-'), DATEADD(day, -1, GETDATE()));

-- 4. Sana Mir (Needs AB+ in Federal B Area)
INSERT INTO [User] (email, password, role) VALUES ('sana@recipient.com', '123456', 'Recipient');
SET @UserId = SCOPE_IDENTITY();
SELECT @AreaId = id FROM Area WHERE name = 'Federal B Area';
INSERT INTO Recipient (name, user_id, bloodtype, area_id, number, DOB, age) 
VALUES ('Sana Mir', @UserId, (SELECT bloodtype_id FROM Blood_Type WHERE type = 'AB+'), @AreaId, '03458887766', '1994-12-12', 30);
SET @RecipientId = SCOPE_IDENTITY();
-- Fulfilled Request (Past)
INSERT INTO Request (recipient_id, units_required, units_collected, status, blood_type, date_requested, date_fulfilled, approved_by)
VALUES (@RecipientId, 2, 2, 'Fulfilled', (SELECT bloodtype_id FROM Blood_Type WHERE type = 'AB+'), DATEADD(day, -10, GETDATE()), DATEADD(day, -9, GETDATE()), @ManagerId);

PRINT 'Expanded demo data inserted successfully.';
GO
