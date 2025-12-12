-- Westmont College CS 125 Database Design Fall 2025
-- Final Project
-- Assistant Professor Mike Ryu
-- Caleb Song & David Oyebade

    USE FP_YG_app;
    -- -------------------------
    -- PERSON
    -- -------------------------
    INSERT INTO Person (FirstName, LastName, Address, DateOfBirth, PhoneNumber) VALUES
    ('John', 'Doe', '123 Elm St', '2008-05-10', '555-111-2222'),
    ('Jane', 'Doe', '123 Elm St', '1978-07-15', '555-111-3333'),
    ('Robert', 'Smith', '456 Oak Ave', '2007-09-12', '555-222-4444'),
    ('Emily', 'Smith', '456 Oak Ave', '1980-04-22', '555-222-5555'),
    ('Michael', 'Brown', '789 Pine Rd', '2006-11-08', '555-333-6666'),
    ('Sarah', 'Brown', '789 Pine Rd', '1982-02-13', '555-333-7777'),
    ('Alex', 'Johnson', '135 Maple Blvd', '2009-01-17', '555-444-8888'),
    ('Chris', 'Johnson', '135 Maple Blvd', '1975-10-10', '555-444-9999'),
    ('David', 'Lee', '246 Cedar St', '2007-03-05', '555-555-0000'),
    ('Linda', 'Lee', '246 Cedar St', '1979-06-30', '555-555-1111'),
    ('Sam', 'Parker', '111 Main St', '2005-12-20', '555-666-2222'),
    ('Julia', 'Parker', '111 Main St', '1983-08-08', '555-666-3333'),
    ('Kevin', 'Wong', '222 Grove St', '2008-02-14', '555-777-4444'),
    ('Amy', 'Wong', '222 Grove St', '1985-09-19', '555-777-5555'),
    ('Daniel', 'Kim', '333 Birch Ln', '2006-07-07', '555-888-6666'),
    ('Grace', 'Kim', '333 Birch Ln', '1984-03-03', '555-888-7777'),
    ('Peter', 'Young', '444 Spruce Dr', '2009-04-21', '555-999-8888'),
    ('Sophia', 'Young', '444 Spruce Dr', '1981-12-12', '555-999-7777'),
    ('Ella', 'Turner', '555 Willow Way', '2007-10-11', '555-000-1234'),
    ('Karen', 'Turner', '555 Willow Way', '1980-01-01', '555-000-2345'),
    ('Jacob', 'Hall', '101 Forest Ct', '2008-06-16', '555-111-5678'),
    ('Lori', 'Hall', '101 Forest Ct', '1978-04-04', '555-111-6789'),
    ('Tyler', 'Adams', '202 Lakeview', '2005-08-09', '555-222-7890'),
    ('Monica', 'Adams', '202 Lakeview', '1983-03-03', '555-222-8901'),
    ('Megan', 'Evans', '303 Hilltop Rd', '2006-09-01', '555-333-9012'),
    ('Donna', 'Evans', '303 Hilltop Rd', '1986-06-06', '555-333-0123'),
    ('Isaac', 'Brooks', '404 River Rd', '2007-12-25', '555-444-1111'),
    ('Patricia', 'Brooks', '404 River Rd', '1981-11-11', '555-444-2222'),
    ('Zach', 'Green', '505 Valley Dr', '2009-02-28', '555-555-3333'),
    ('Michelle', 'Green', '505 Valley Dr', '1982-08-23', '555-555-4444'),
    ('Anthony', 'King', '606 Ocean Blvd', '2006-04-30', '555-666-5555'),
    ('Rachel', 'King', '606 Ocean Blvd', '1984-02-14', '555-666-6666'),
    ('Jason', 'Scott', '707 Sunrise Ave', '2005-09-19', '555-777-7777'),
    ('Laura', 'Scott', '707 Sunrise Ave', '1987-07-07', '555-777-8888');

    -- -------------------------
    -- STUDENTS
    -- -------------------------
    INSERT INTO Student (StudentID, Grade) VALUES
    (1, 9), (3, 8), (5, 10), (7, 7), (9, 8), (11, 12), (13, 9), (15, 11),
    (17, 7), (19, 8), (21, 9), (23, 12), (25, 10), (27, 8), (29, 7),
    (31, 11), (33, 12);

    -- -------------------------
    -- PARENTS
    -- -------------------------
    INSERT INTO Parent (ParentID) VALUES
    (2), (4), (6), (8), (10), (12), (14), (16), (18), (20),
    (22), (24), (26), (28), (30), (32), (34);

    -- -------------------------
    -- STUDENT ↔ PARENT
    -- -------------------------
    INSERT INTO StudentParent (StudentID, ParentID) VALUES
    (1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16),
    (17,18),(19,20),(21,22),(23,24),(25,26),(27,28),(29,30),
    (31,32),(33,34);

    -- -------------------------
    -- VOLUNTEERS
    -- -------------------------
    INSERT INTO Volunteer (VolunteerID) VALUES
    (12),(14),(16),(18),(20);

    -- -------------------------
    -- LEADERS
    -- -------------------------
    INSERT INTO Leader (LeaderID, Title) VALUES
    (22, 'Youth Pastor'),
    (24, 'Assistant Director'),
    (26, 'Small Group Coach'),
    (28, 'Program Coordinator'),
    (30, 'Event Manager');

    -- -------------------------
    -- SMALL GROUPS
    -- -------------------------
    INSERT INTO SmallGroup (Name, MeetingTime) VALUES
    ('Middle School Boys', '18:00:00'),
    ('Middle School Girls', '18:00:00'),
    ('High School Boys', '19:00:00'),
    ('High School Girls', '19:00:00'),
    ('College Prep Group', '20:00:00');

    -- -------------------------
    -- PERSON ↔ GROUP
    -- -------------------------
    INSERT INTO PersonGroup (PersonID, SmallGroupID) VALUES
    (1,1),(3,1),(7,1),(9,1),
    (13,2),(17,2),(19,2),
    (11,3),(15,3),(21,3),
    (25,4),(27,4),(29,4),
    (31,5),(33,5);

    -- -------------------------
    -- PLACE
    -- -------------------------
    INSERT INTO Place (Name, Address) VALUES
    ('Youth Center', '800 Youth Dr'),
    ('Community Park', '122 Park Ln'),
    ('Retreat Center', '999 Mountain Rd'),
    ('Main Sanctuary', '500 Church Ave'),
    ('Activity Hall', '700 Activity Blvd');

    -- -------------------------
    -- EVENT TYPES (NEW)
    -- -------------------------
    INSERT INTO EventType (Name) VALUES
    ('Weekly Youth Night'),
    ('Off-Site Retreat'),
    ('Service Project'),
    ('Program Training/Meeting'),
    ('Social/Party');

    -- -------------------------
    -- EVENTS (UPDATED WITH TypeID)
    -- -------------------------
    -- Insert Events (10 total, matching MongoDB)
    INSERT INTO Event (Name, EventTypeID, PlaceID, StartDateTime, EndDateTime) VALUES
    -- 1
    ('Weekly Youth Night - Jan', 1, 1, '2025-01-10 18:00:00', '2025-01-10 21:00:00'),
    -- 2
    ('Weekly Youth Night - Feb', 1, 1, '2025-02-14 18:00:00', '2025-02-14 21:00:00'),
    -- 3
    ('Spring Retreat', 2, 2, '2025-03-21 17:00:00', '2025-03-23 12:00:00'),
    -- 4
    ('Service Project', 3, 3, '2025-04-12 09:00:00', '2025-04-12 15:00:00'),
    -- 5
    ('Summer Kickoff', 5, 1, '2025-06-10 16:00:00', '2025-06-10 20:00:00'),
    -- 6
    ('Back-to-School Bash', 5, 1, '2025-08-20 17:00:00', '2025-08-20 20:30:00'),
    -- 7
    ('Christmas Party', 5, 1, '2025-12-15 18:00:00', '2025-12-15 21:00:00'),
    -- 8
    ('Volunteer Training', 4, 4, '2025-09-05 18:00:00', '2025-09-05 20:00:00'),
    -- 9
    ('Parent Info Night', 4, 4, '2025-09-12 18:00:00', '2025-09-12 19:30:00'),
    -- 10
    ('Outreach Booth', 3, 3, '2025-10-05 10:00:00', '2025-10-05 15:00:00');


    -- -------------------------
    -- REGISTRATIONS
    -- -------------------------
    INSERT INTO Registration (StudentID, EventID, RegistrantID) VALUES
    (1,1,2),(3,1,4),(5,1,6),(7,1,8),
    (1,2,2),(3,2,4),(5,2,6),
    (1,3,2),(3,3,4),(5,3,6),(7,3,8),
    (9,4,10),(11,4,12),
    (13,5,14),(15,5,16),(17,5,18),
    (19,6,20),(21,6,22),
    (23,7,24),(25,7,26),(27,7,28),
    (29,8,30),(31,8,32),
    (33,9,34);

    -- -------------------------
    -- TASKS
    -- -------------------------
    INSERT INTO Task (Description) VALUES
    ('Setup Chairs'),
    ('Serve Food'),
    ('Lead Small Group'),
    ('Cleanup'),
    ('Welcome Team');

    -- -------------------------
    -- SHIFT CALENDAR
    -- -------------------------
    INSERT INTO ShiftCalender (VolunteerID, LeaderID, EventID, Scheduled, TaskID) VALUES
    (12,22,1,TRUE,1),
    (14,24,2,TRUE,2),
    (16,26,3,TRUE,3),
    (18,28,4,TRUE,4),
    (20,30,5,TRUE,5);

    -- -------------------------
    -- ATTENDEES
    -- -------------------------
    INSERT INTO Attendee (RegistrationID, CheckInTime, CheckOutTime) VALUES
    (1,'18:00','21:00'),
    (2,'18:10','21:00'),
    (3,'18:20','21:00'),
    (4,'18:30','21:00'),
    (5,'18:00','21:00');
