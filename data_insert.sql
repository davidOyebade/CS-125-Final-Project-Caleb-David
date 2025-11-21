-- Dataset population script for FP_YG_app (FirstName + LastName)
-- TRUNCATE tables in FK-safe order, then multi-row INSERTs (implicit IDs)
USE FP_YG_app;

-- 1) TRUNCATE (FK-safe order)
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Attendee;
TRUNCATE TABLE ShiftCalender;
TRUNCATE TABLE Registration;
TRUNCATE TABLE PersonGroup;
TRUNCATE TABLE StudentParent;
TRUNCATE TABLE Student;
TRUNCATE TABLE Parent;
TRUNCATE TABLE Volunteer;
TRUNCATE TABLE Leader;
TRUNCATE TABLE Event;
TRUNCATE TABLE SmallGroup;
TRUNCATE TABLE Place;
TRUNCATE TABLE Task;
TRUNCATE TABLE Person;

SET FOREIGN_KEY_CHECKS = 1;


-- 2) INSERT Persons (45 persons) -- implicit IDs (1..45)
INSERT INTO Person (FirstName, LastName, Address, DateOfBirth, PhoneNumber) VALUES
('John','Smith',        '101 Oak St',   '2008-05-12', '555-101-0001'),
('Sarah','Johnson',     '102 Oak St',   '2009-07-03', '555-101-0002'),
('Michael','Williams',  '103 Oak St',   '2007-11-21', '555-101-0003'),
('Emily','Brown',       '104 Oak St',   '2008-02-19', '555-101-0004'),
('David','Jones',       '105 Oak St',   '2006-09-09', '555-101-0005'),
('Olivia','Garcia',     '106 Oak St',   '2009-12-30', '555-101-0006'),
('Daniel','Miller',     '107 Oak St',   '2007-03-17', '555-101-0007'),
('Ava','Davis',         '108 Oak St',   '2008-06-25', '555-101-0008'),
('James','Rodriguez',   '109 Oak St',   '2006-01-14', '555-101-0009'),
('Isabella','Martinez', '110 Oak St',   '2009-04-08', '555-101-0010'),
('Ethan','Hernandez',   '111 Oak St',   '2008-08-02', '555-101-0011'),
('Mia','Lopez',         '112 Oak St',   '2007-10-30', '555-101-0012'),
('Alexander','Gonzalez','113 Oak St',   '2009-03-10', '555-101-0013'),
('Sophia','Wilson',     '114 Oak St',   '2008-01-05', '555-101-0014'),
('Benjamin','Anderson', '115 Oak St',   '2007-12-12', '555-101-0015'),
('Charlotte','Thomas',  '116 Oak St',   '2006-07-22', '555-101-0016'),
('Matthew','Taylor',    '117 Oak St',   '2009-09-09', '555-101-0017'),
('Amelia','Moore',      '118 Oak St',   '2008-11-11', '555-101-0018'),
('Joseph','Jackson',    '119 Oak St',   '2007-02-02', '555-101-0019'),
('Harper','Martin',     '120 Oak St',   '2009-06-06', '555-101-0020'),
('Samuel','Lee',        '121 Oak St',   '2008-04-04', '555-101-0021'),
('Ella','Perez',        '122 Oak St',   '2007-08-08', '555-101-0022'),
-- Parents (IDs 23 - 40)
('Karen','Young',       '201 Pine Ave', '1980-03-20', '555-201-0001'),
('Robert','King',       '202 Pine Ave', '1978-10-10', '555-201-0002'),
('Patricia','Wright',   '203 Pine Ave', '1982-06-06', '555-201-0003'),
('Thomas','Scott',      '204 Pine Ave', '1976-01-01', '555-201-0004'),
('Linda','Green',       '205 Pine Ave', '1981-04-04', '555-201-0005'),
('Charles','Adams',     '206 Pine Ave', '1979-12-12', '555-201-0006'),
('Barbara','Baker',     '207 Pine Ave', '1983-09-09', '555-201-0007'),
('Steven','Nelson',     '208 Pine Ave', '1977-07-07', '555-201-0008'),
('Susan','Carter',      '209 Pine Ave', '1984-05-05', '555-201-0009'),
('Edward','Mitchell',   '210 Pine Ave', '1975-11-11', '555-201-0010'),
('Jessica','Perez',     '211 Pine Ave', '1980-08-08', '555-201-0011'),
('Andrew','Roberts',    '212 Pine Ave', '1976-02-02', '555-201-0012'),
('Laura','Turner',      '213 Pine Ave', '1982-03-03', '555-201-0013'),
('Mark','Phillips',     '214 Pine Ave', '1979-06-06', '555-201-0014'),
('Kimberly','Campbell', '215 Pine Ave', '1981-07-07', '555-201-0015'),
('Paul','Parker',       '216 Pine Ave', '1978-09-09', '555-201-0016'),
('Nancy','Evans',       '217 Pine Ave', '1983-02-02', '555-201-0017'),
('George','Edwards',    '218 Pine Ave', '1975-05-05', '555-201-0018'),
-- Volunteers (IDs 41 - 44 are volunteers duplicated from parent block if desired, but we'll add distinct volunteer persons)
('Volunteer','A',       '301 Church Rd', '1995-11-11', '555-301-0001'),
('Volunteer','B',       '302 Church Rd', '1990-10-10', '555-301-0002'),
('Leader','Anna',       '401 Church Rd', '1988-08-08', '555-401-0001'),
('Leader','Ben',        '402 Church Rd', '1985-05-05', '555-401-0002'),
('Leader','Cara',       '403 Church Rd', '1982-02-02', '555-401-0003');

-- (Total persons inserted: 45)


-- 3) INSERT Student rows (StudentID references Person.ID)
-- Students are Person IDs 1..22
INSERT INTO Student (StudentID, Grade) VALUES
(1,  9),
(2, 10),
(3, 11),
(4, 10),
(5, 12),
(6,  9),
(7, 11),
(8, 10),
(9, 12),
(10, 9),
(11, 11),
(12, 12),
(13, 10),
(14, 11),
(15, 12),
(16, 9),
(17, 10),
(18, 11),
(19, 12),
(20, 9),
(21, 11),
(22, 12);


-- 4) INSERT Parent rows (ParentID references Person.ID)
-- Parents are Person IDs 23..40
INSERT INTO Parent (ParentID) VALUES
(23),(24),(25),(26),(27),(28),(29),(30),
(31),(32),(33),(34),(35),(36),(37),(38),
(39),(40);


-- 5) INSERT Volunteer rows (VolunteerID references Person.ID)
-- Volunteers assigned to Person IDs 41..44 and also reuse some parent IDs for volunteers (to reach 10 volunteers, we'll reuse 31..36 as volunteers as well)
INSERT INTO Volunteer (VolunteerID) VALUES
(31),(32),(33),(34),(35),(36),(41),(42),(43),(44);


-- 6) INSERT Leader rows (LeaderID references Person.ID, plus Title)
-- Leaders are Person IDs 45..49? We only have up to 45 persons; to keep within 45, assign leaders to 41..45 where 41..44 are volunteers/leader names and 45 is 'Leader Cara' inserted above.
-- For clarity, we'll declare leaders as IDs 41..45 (some persons double as both volunteer/leader conceptually but stored in respective tables)
INSERT INTO Leader (LeaderID, Title) VALUES
(41, 'Youth Pastor'),
(42, 'Small Group Leader'),
(43, 'Assistant Leader'),
(44, 'Worship Leader'),
(45, 'Program Director');


-- 7) INSERT StudentParent (many-to-many)
-- Roughly 22 students with 1-2 parents each; parents chosen cyclically from 23..40
INSERT INTO StudentParent (StudentID, ParentID) VALUES
(1, 23),(1,24),
(2, 25),
(3, 26),(3,27),
(4, 28),
(5, 29),(5,30),
(6, 31),
(7, 32),(7,33),
(8, 34),
(9, 35),(9,36),
(10,37),
(11,38),(11,39),
(12,40),
(13,23),
(14,24),(14,25),
(15,26),
(16,27),
(17,28),
(18,29),
(19,30),
(20,31),
(21,32),
(22,33);


-- 8) INSERT SmallGroup (6 groups)
INSERT INTO SmallGroup (Name, MeetingTime) VALUES
('Jr High Boys', '18:30:00'),
('Jr High Girls','18:30:00'),
('High School Guys','19:00:00'),
('High School Girls','19:00:00'),
('Service Team','20:00:00'),
('Newcomers','18:00:00');


-- 9) INSERT PersonGroup (assign people to groups)
-- We'll assign students and some leaders/volunteers to groups
INSERT INTO PersonGroup (PersonID, SmallGroupID) VALUES
-- Group 1: Jr High Boys (students 1,5,10,16)
(1,1),(5,1),(10,1),(16,1),
-- Group 2: Jr High Girls (students 2,6,11,20)
(2,2),(6,2),(11,2),(20,2),
-- Group 3: High School Guys (students 3,7,9,13,21)
(3,3),(7,3),(9,3),(13,3),(21,3),
-- Group 4: High School Girls (students 4,8,12,14,22)
(4,4),(8,4),(12,4),(14,4),(22,4),
-- Group 5: Service Team (volunteers 31..36 plus students 15,17)
(31,5),(32,5),(33,5),(34,5),(35,5),(36,5),(15,5),(17,5),
-- Group 6: Newcomers (leaders 41,42 and some parents 23,24)
(41,6),(42,6),(23,6),(24,6);


-- 10) INSERT Place (5 places)
INSERT INTO Place (Name, Address) VALUES
('Main Hall', '1 Campus Drive'),
('Youth Room','2 Campus Drive'),
('Gym', '3 Campus Drive'),
('Offsite Park', '45 Park Lane'),
('Cafeteria', '4 Campus Drive');


-- 11) INSERT Event (10 events)
-- PlaceID references the Place table created above (1..5)
-- Use varied Start/End datetimes (YYYY-MM-DD HH:MM:SS)
INSERT INTO Event (Name, PlaceID, StartDateTime, EndDateTime) VALUES
('Weekly Youth Night - Jan',     2, '2025-01-12 18:30:00', '2025-01-12 21:00:00'),
('Weekly Youth Night - Feb',     2, '2025-02-09 18:30:00', '2025-02-09 21:00:00'),
('Spring Retreat',               4, '2025-03-21 09:00:00', '2025-03-23 15:00:00'),
('Service Project',              5, '2025-04-05 08:00:00', '2025-04-05 17:00:00'),
('Summer Kickoff',               1, '2025-06-07 16:00:00', '2025-06-07 22:00:00'),
('Back-to-School Bash',          3, '2025-08-20 17:00:00', '2025-08-20 20:00:00'),
('Christmas Party',              2, '2025-12-14 18:00:00', '2025-12-14 21:00:00'),
('Volunteer Training',           1, '2025-05-10 09:00:00', '2025-05-10 12:00:00'),
('Parent Info Night',            1, '2025-09-15 19:00:00', '2025-09-15 20:30:00'),
('Outreach Booth',               4, '2025-07-04 10:00:00', '2025-07-04 14:00:00');


-- 12) INSERT Task (10 tasks)
INSERT INTO Task (Description) VALUES
('Check-In Desk'),
('Welcome & Seating'),
('Audio/Visual Setup'),
('Worship Setup'),
('Kitchen Support'),
('Small Group Facilitation'),
('Transportation Coordination'),
('First Aid/Medications'),
('Service Project Lead'),
('Cleanup');


-- 13) INSERT Registration (unique StudentID,EventID) -- ~70 rows
-- We'll register students across events (each student signs up for ~3-4 events)
-- RegistrantID is usually a parent (from StudentParent mapping) or the student themselves for older students.
INSERT INTO Registration (StudentID, EventID, RegistrantID) VALUES
-- Student 1 (ID=1) registers for event 1,3,5
(1, 1, 23),(1, 3, 23),(1, 5, 23),
-- Student 2
(2, 1, 24),(2, 4, 24),(2, 6, 24),
-- Student 3
(3, 1, 26),(3, 3, 26),(3, 5, 26),
-- Student 4
(4, 2, 28),(4, 5, 28),
-- Student 5
(5, 1, 29),(5, 3, 29),(5, 7, 29),
-- Student 6
(6, 2, 31),(6, 5, 31),
-- Student 7
(7, 3, 33),(7, 5, 33),(7, 6, 33),
-- Student 8
(8, 1, 34),(8, 2, 34),(8, 7, 34),
-- Student 9
(9, 4, 35),(9, 5, 35),(9, 10,35),
-- Student 10
(10,1, 37),(10,2, 37),
-- Student 11
(11,3, 38),(11,5, 38),
-- Student 12
(12,3, 40),(12,7, 40),
-- Student 13
(13,1, 23),(13,6, 23),
-- Student 14
(14,2, 24),(14,8, 24),
-- Student 15
(15,3, 26),(15,5, 26),(15,9, 26),
-- Student 16
(16,4, 27),(16,5, 27),
-- Student 17
(17,1, 28),(17,2, 28),(17,3, 28),
-- Student 18
(18,5, 29),(18,7, 29),
-- Student 19
(19,6, 30),(19,9, 30),
-- Student 20
(20,1, 31),(20,4, 31),
-- Student 21
(21,2, 32),(21,5, 32),(21,10,32),
-- Student 22
(22,1, 33),(22,3, 33);

-- Additional registrations to reach ~70 entries: add more students to repeat events (ensuring uniqueness per student/event)
INSERT INTO Registration (StudentID, EventID, RegistrantID) VALUES
(1, 2, 23),(2, 3, 24),(3, 2, 26),(4, 3, 28),(5, 2, 29),
(6, 1, 31),(7, 4, 33),(8, 4, 34),(9, 2, 35),(10,3, 37),
(11,2, 38),(12,1, 40),(13,3, 23),(14,1, 24),(15,2, 26),
(16,2, 27),(17,4, 28),(18,1, 29),(19,1, 30),(20,3, 31),
(21,1, 32),(22,2, 33),(5, 8, 29),(7, 8, 33),(11, 8, 38),
(13, 9, 23),(15, 10, 26),(18, 9, 29),(20, 9, 31),(9, 6, 35),
(3, 6, 26),(12, 6, 40),(17, 6, 28),(4, 6, 28),(2, 9, 24);


-- 14) INSERT ShiftCalender (20 shifts) -- XOR: either VolunteerID OR LeaderID is set, not both
-- Columns: (VolunteerID, LeaderID, EventID, Scheduled, TaskID)
-- Volunteers: 31..36,41..44 ; Leaders: 41..45 ; Events: 1..10 ; Tasks: 1..10
INSERT INTO ShiftCalender (VolunteerID, LeaderID, EventID, Scheduled, TaskID) VALUES
-- Volunteer shifts
(31, NULL, 1, TRUE, 1),
(32, NULL, 1, TRUE, 2),
(33, NULL, 3, TRUE, 9),
(34, NULL, 3, TRUE, 3),
(35, NULL, 4, TRUE, 5),
(36, NULL, 4, TRUE, 9),
(41, NULL, 5, TRUE, 4),
(42, NULL, 5, TRUE, 10),
(43, NULL, 6, TRUE, 1),
(44, NULL, 6, TRUE, 2),
-- Leader shifts (no volunteer listed)
(NULL, 41, 1, TRUE, 2),
(NULL, 42, 3, TRUE, 6),
(NULL, 43, 5, TRUE, 4),
(NULL, 44, 7, TRUE, 4),
(NULL, 45, 8, TRUE, 3),
(NULL, 41, 9, TRUE, 9),
(NULL, 42, 10, TRUE, 8),
(NULL, 43, 2, TRUE, 7),
(NULL, 44, 4, TRUE, 5),
(NULL, 45, 6, TRUE, 10);


-- 15) INSERT Attendee (some subset of Registrations checked in)
-- Attendee has RegistrationID (references Registration.ID), CheckInTime, CheckOutTime
-- Registration IDs are auto-incremented starting from 1 in the order the Registration rows were inserted.
-- We'll mark the first 36 registration IDs as attendees (a realistic subset).
INSERT INTO Attendee (RegistrationID, CheckInTime, CheckOutTime) VALUES
(1, '18:20:00', '21:00:00'),
(2, '08:30:00', '15:00:00'),
(3, '16:00:00', '21:00:00'),
(4, '18:20:00', '21:00:00'),
(5, '18:20:00', '21:00:00'),
(6, '18:20:00', '21:00:00'),
(7, '18:20:00', '21:00:00'),
(8, '18:20:00', '21:00:00'),
(9, '09:00:00', '15:00:00'),
(10,'08:00:00', '17:00:00'),
(11,'18:20:00', '21:00:00'),
(12,'18:20:00', '21:00:00'),
(13,'18:20:00', '21:00:00'),
(14,'18:20:00', '21:00:00'),
(15,'09:00:00', '12:00:00'),
(16,'08:30:00', '15:00:00'),
(17,'16:00:00', '21:00:00'),
(18,'18:20:00', '21:00:00'),
(19,'18:20:00', '21:00:00'),
(20,'18:20:00', '21:00:00'),
(21,'09:00:00', '15:00:00'),
(22,'16:00:00', '21:00:00'),
(23,'18:20:00', '21:00:00'),
(24,'18:20:00', '21:00:00'),
(25,'18:20:00', '21:00:00'),
(26,'08:30:00', '12:00:00'),
(27,'09:00:00', '15:00:00'),
(28,'16:00:00', '21:00:00'),
(29,'18:20:00', '21:00:00'),
(30,'18:20:00', '21:00:00'),
(31,'09:00:00', '15:00:00'),
(32,'18:20:00', '21:00:00'),
(33,'18:20:00', '21:00:00'),
(34,'08:30:00', '12:00:00'),
(35,'09:00:00', '15:00:00'),
(36,'16:00:00', '21:00:00');


-- End of dataset population
-- You can now query tables: Person, Student, Parent, Volunteer, Leader, SmallGroup, Event, Registration, ShiftCalender, Attendee, etc.
