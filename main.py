#Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
# Caleb Song & David Oyebade


import mysql.connector
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import redis
from datetime import datetime
from typing import Optional, Dict, Any
import traceback
import logging
from dotenv import load_dotenv
from mongodb_implement import get_mongo_client, get_mongo_db
from redis_implement import get_redis_client, get_redis_conn

# --- Database Configuration ---
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASS")
DB_HOST = "mysql"
DB_NAME = "FP_YG_app"

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# --- Connection Pooling ---
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="fastapi_pool",
        pool_size=5,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    exit()
mongoDBclient = get_mongo_client()
redisClient = get_redis_client()


# --- FastAPI App ---
app = FastAPI(
    title="Youth Group API",
    description="An API for interacting with the FP_YG_app database.",
    version="1.0.0"
)

try:
    from graphql_app import graphql_app, init_graphql
    # Initialize GraphQL with database connections
    init_graphql(db_pool, redisClient, mongoDBclient)
    app.include_router(graphql_app, prefix="/graphql")
    print("✓ GraphQL endpoint available at /graphql")
except ImportError as e:
    print(f"⚠ GraphQL not available - install strawberry-graphql: pip install strawberry-graphql")
    print(f"  Import error: {e}")
except Exception as e:
    print(f"⚠ GraphQL integration error: {e}")

# --- Pydantic Models (for request/response validation) ---
class Person(BaseModel):
    id: int
    firstName: str
    lastName: str

class Event(BaseModel):
    id: int
    name: str

class SmallGroup(BaseModel):
    id: int
    name: str
class Student(BaseModel):
    id: int
    firstName: str
    lastName: str
    grade: int
class Parent(BaseModel):
    parentID: int
    firstName: str
    lastName: str

class VolunteerOutput(BaseModel):
    volunteerID: int
    firstName: str
    lastName: str

class LeaderOutput(BaseModel):
    leaderID: int
    firstName: str
    lastName: str
    title: str | None = None

class ShiftAssign(BaseModel):
    volunteerID: int | None = None
    leaderID: int | None = None
    taskID: int
    scheduled: bool = True

class CustomFieldDefinition(BaseModel):
    field_name: str
    data_type: str # e.g., "text", "number", "boolean"

# Input model for creating a new user-defined event type.
class EventTypeCreate(BaseModel):
    name: str
    custom_fields: list[CustomFieldDefinition]

# Model for creating an event with custom field values
class EventCreate(BaseModel):
    name: str
    event_type_id: int
    place_id: int
    start_date_time: str  # ISO format datetime string
    end_date_time: str    # ISO format datetime string
    custom_field_values: Optional[Dict[str, Any]] = None  # Custom field values

# Model for event type response with schema
class EventTypeResponse(BaseModel):
    event_type_id: int
    name: str
    custom_fields: list[CustomFieldDefinition]

# Model for event response with custom data
class EventWithCustomData(BaseModel):
    id: int
    name: str
    event_type_id: int
    place_id: int
    start_date_time: Optional[str]
    end_date_time: Optional[str]
    custom_field_values: Optional[Dict[str, Any]] = None

# Model for updating an event's custom field values
class EventCustomDataUpdate(BaseModel):
    custom_field_values: Dict[str, Any]

# --- API Endpoints ---
@app.get("/")
def read_root():
    """
    Root endpoint with a welcome message.
    """
    return {"message": "Welcome to the Youth Group API!"}

@app.get("/people", response_model=list[Person])
def get_all_people():
    """
    Retrieves a list of all people.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, firstName, lastName FROM Person ORDER BY lastName, firstName;")
        people = cursor.fetchall()
        return people
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/people/search", response_model=list[Person])
def search_people_by_name(name: str):
    """
    Search for people by first or last name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT id, firstName, lastName
            FROM Person
            WHERE LOWER(firstName) LIKE LOWER(%s)
               OR LOWER(lastName) LIKE LOWER(%s)
            ORDER BY lastName, firstName;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard, wildcard))

        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/people/{person_id}", response_model=Person)
def get_person_by_id(person_id: int):
    """
    Retrieves a specific customer by their ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, firstName, lastName FROM Person WHERE id = %s;"
        cursor.execute(query, (person_id,))
        person = cursor.fetchone()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
@app.get("/people/{person_id}/smallgroups")
def get_smallgroups_for_person(person_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT SmallGroup.id, SmallGroup.name
            FROM PersonGroup
            JOIN SmallGroup ON PersonGroup.smallGroupID = SmallGroup.id
            WHERE personID = %s;
        """
        cursor.execute(query, (person_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()


@app.get("/parents", response_model=list[Parent])
def get_all_parents():
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT Parent.parentID, firstName, lastName
            FROM Parent 
            JOIN Person ON Parent.parentID = Person.id;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/parents/search", response_model=list[Parent])
def search_parents_by_name(name: str):
    """
    Search for parents by first or last name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT p.id AS parentID, p.firstName, p.lastName
            FROM Parent pr
            JOIN Person p ON pr.parentID = p.id
            WHERE LOWER(p.firstName) LIKE LOWER(%s)
               OR LOWER(p.lastName) LIKE LOWER(%s)
            ORDER BY p.lastName, p.firstName;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard, wildcard))

        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/parents/{parent_id}", response_model=Parent)
def get_parent_by_id(parent_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT parentID, firstName, lastName
            FROM Parent JOIN Person ON parentID = id
            WHERE parentID = %s;
        """
        cursor.execute(query, (parent_id,))
        parent = cursor.fetchone()
        if not parent:
            raise HTTPException(404, "Parent not found")
        return parent
    finally:
        cursor.close()
        cnx.close()
@app.get("/parents/{parent_id}/students", response_model=list[Student])
def get_students_of_parent(parent_id: int):
    """
    Retrieves all students associated with a given parent
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT p.id AS id, p.firstName, p.lastName, s.grade
            FROM StudentParent sp
            JOIN Student s ON sp.studentID = s.studentID
            JOIN Person p ON s.studentID = p.id
            WHERE sp.parentID = %s
            ORDER BY p.lastName, p.firstName;
        """

        cursor.execute(query, (parent_id,))
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()





@app.get("/students", response_model=list[Student])
def get_all_students():
    """
    Retrieves a list of all students
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, firstName, lastName, grade FROM Person JOIN Student ON Student.studentID = Person.id  ORDER BY lastName, firstName;")
        students = cursor.fetchall()
        return students
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/students/search", response_model=list[Student])
def search_students_by_name(name: str):
    """
    Search for students by first or last name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT 
                p.id, p.firstName, p.lastName, s.grade
            FROM Person p
            JOIN Student s ON s.studentID = p.id
            WHERE LOWER(p.firstName) LIKE LOWER(%s)
               OR LOWER(p.lastName) LIKE LOWER(%s)
            ORDER BY p.lastName, p.firstName;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard, wildcard))

        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()

@app.get("/students/grade/{student_grade}", response_model=list[Student])
def get_students_by_grade(student_grade: int):
    """
    Retrieve students by grade
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, firstName, lastName, grade FROM Person JOIN Student ON Student.studentID = Person.id WHERE Grade = %s ORDER BY lastName, firstName;"
        cursor.execute(query, (student_grade,))
        students = cursor.fetchall()
        if not students:
            raise HTTPException(status_code=404, detail="Grade not found")
        return students
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
@app.get("/students/{student_id}", response_model=Student)
def get_student_by_id(student_id: int):
    """
    Retrieves a specific student by their ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, firstName, lastName, grade FROM Person JOIN Student ON Student.studentID = Person.id WHERE id = %s;"
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/students/{student_id}/parents", response_model=list[Parent])
def get_parents_of_student(student_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT Parent.parentID AS parentID, firstName, lastName
            FROM StudentParent
            JOIN Parent ON Parent.parentID = StudentParent.parentID
            JOIN Person ON Parent.parentID = Person.id
            WHERE StudentParent.StudentID = %s;
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()


@app.get("/events", response_model=list[Event])
def get_all_events():
    """
    Retrieves a list of all products.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM Event ORDER BY name;")
        events = cursor.fetchall()
        return events
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/events/search", response_model=list[Event])
def search_events_by_name(name: str):
    """
    Search for events by name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT id, name
            FROM Event
            WHERE LOWER(name) LIKE LOWER(%s)
            ORDER BY name;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard,))

        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
@app.get("/events/{event_id}", response_model=Event)
def get_event_by_id(event_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, name FROM Event WHERE id = %s;"
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.post("/events/{event_id}/assign", status_code=201)
def assign_to_event(event_id: int, data: ShiftAssign):
    """
    Assign a volunteer or leader to an event with a specific task.
    Exactly one of volunteerID or leaderID must be provided.
    """
    if (data.volunteerID is None) == (data.leaderID is None):
        raise HTTPException(400, "Provide either volunteerID OR leaderID, not both")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute("""
            INSERT INTO ShiftCalender (VolunteerID, LeaderID, EventID, Scheduled, TaskID)
            VALUES (%s, %s, %s, %s, %s);
        """, (data.volunteerID, data.leaderID, event_id, data.scheduled, data.taskID))

        cnx.commit()

        return {"message": "Assigned successfully"}

    finally:
        cursor.close()
        cnx.close()
@app.get("/events/{event_id}/workers")
def get_event_workers(event_id: int):
    """
    Returns all volunteers and leaders assigned to an event, with task info.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # ---- GET VOLUNTEERS ----
        cursor.execute("""
            SELECT 
                sc.ID AS shiftID,
                p.ID AS personID,
                p.firstName,
                p.lastName,
                t.ID AS taskID,
                t.Description AS taskDescription,
                'volunteer' AS role
            FROM ShiftCalender sc
            JOIN Volunteer v ON sc.VolunteerID = v.VolunteerID
            JOIN Person p ON p.ID = v.VolunteerID
            JOIN Task t ON sc.TaskID = t.ID
            WHERE sc.EventID = %s;
        """, (event_id,))
        volunteers = cursor.fetchall()

        # ---- GET LEADERS ----
        cursor.execute("""
            SELECT 
                sc.ID AS shiftID,
                p.ID AS personID,
                p.firstName,
                p.lastName,
                l.Title AS leaderTitle,
                t.ID AS taskID,
                t.Description AS taskDescription,
                'leader' AS role
            FROM ShiftCalender sc
            JOIN Leader l ON sc.LeaderID = l.LeaderID
            JOIN Person p ON p.ID = l.LeaderID
            JOIN Task t ON sc.TaskID = t.ID
            WHERE sc.EventID = %s;
        """, (event_id,))
        leaders = cursor.fetchall()

        return {
            "event_id": event_id,
            "workers": volunteers + leaders
        }

    finally:
        cursor.close()
        cnx.close()

@app.get("/events/{event_id}/roster")
def get_event_roster(event_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT Registration.id AS RegistrationID, Student.studentID, firstName, lastName
            FROM Registration
            JOIN Student ON Registration.studentID = Student.studentID
            JOIN Person ON Student.studentID = Person.id
            WHERE eventID = %s;
        """
        cursor.execute(query, (event_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/smallgroups", response_model=list[SmallGroup])
def get_all_smallgroups():
    """
    Retrieves a list of all products.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM SmallGroup ORDER BY name;")
        smallgroups = cursor.fetchall()
        return smallgroups
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/smallgroups/search", response_model=list[SmallGroup])
def search_smallgroups_by_name(name: str):
    """
    Search for small groups by name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT id, name
            FROM SmallGroup
            WHERE LOWER(name) LIKE LOWER(%s)
            ORDER BY name;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard,))

        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
@app.get("/smallgroups/{smallgroup_id}", response_model=SmallGroup)
def get_smallgroup_by_id(smallgroup_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, name FROM SmallGroup WHERE id = %s;"
        cursor.execute(query, (smallgroup_id,))
        smallgroup = cursor.fetchone()
        if not smallgroup:
            raise HTTPException(status_code=404, detail="smallgroup not found")
        return smallgroup
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
@app.get("/smallgroups/{group_id}/roster")
def get_small_group_roster(group_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT Person.id, firstName, lastName
            FROM PersonGroup
            JOIN Person ON PersonGroup.personID = Person.id
            WHERE smallGroupID = %s
            ORDER BY lastName, firstName;
        """, (group_id,))

        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.post("/smallgroups/{group_id}/add/{person_id}")
def add_person_to_small_group(group_id: int, person_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute(
            "INSERT INTO PersonGroup(personID, smallGroupID) VALUES (%s, %s);",
            (person_id, group_id)
        )
        cnx.commit()
        return {"message": "Person added to group"}
    except mysql.connector.Error as err:
        raise HTTPException(400, str(err))
    finally:
        cursor.close()
        cnx.close()

@app.delete("/smallgroups/{group_id}/remove/{person_id}")
def remove_person_from_small_group(group_id: int, person_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute(
            "DELETE FROM PersonGroup WHERE personID = %s AND smallGroupID = %s;",
            (person_id, group_id)
        )
        cnx.commit()
        return {"message": "Person removed from group"}
    finally:
        cursor.close()
        cnx.close()
@app.get("/volunteers", response_model=list[VolunteerOutput])
def get_volunteers():
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT volunteerID, firstName, lastName
            FROM Volunteer JOIN Person ON volunteerID = id;
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()
@app.get("/volunteers/search", response_model=list[VolunteerOutput])
def search_volunteers_by_name(name: str):
    """
    Search for volunteers by first or last name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT v.volunteerID, p.firstName, p.lastName
            FROM Volunteer v
            JOIN Person p ON v.volunteerID = p.id
            WHERE LOWER(p.firstName) LIKE LOWER(%s)
               OR LOWER(p.lastName) LIKE LOWER(%s)
            ORDER BY p.lastName, p.firstName;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard, wildcard))
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/volunteers/{volunteer_id}", response_model=VolunteerOutput)
def get_volunteer_by_id(volunteer_id: int):
    """
    Retrieve a volunteer by exact ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT v.volunteerID, p.firstName, p.lastName
            FROM Volunteer v
            JOIN Person p ON v.volunteerID = p.id
            WHERE v.volunteerID = %s;
        """

        cursor.execute(query, (volunteer_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Volunteer not found")

        return result

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/volunteers/{volunteer_id}/tasks")
def get_volunteer_tasks(volunteer_id: int):
    """
    Returns all tasks a volunteer is assigned, across all events.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sc.ID AS shiftID,
                e.ID AS eventID,
                e.Name AS eventName,
                e.StartDateTime,
                e.EndDateTime,
                t.ID AS taskID,
                t.Description AS taskDescription
            FROM ShiftCalender sc
            JOIN Event e ON e.ID = sc.EventID
            JOIN Task t ON t.ID = sc.TaskID
            WHERE sc.VolunteerID = %s;
        """, (volunteer_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        cnx.close()


@app.get("/leaders", response_model=list[LeaderOutput])
def get_all_leaders():
    """
    Retrieve a list of all leaders.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT Leader.leaderID, Person.firstName, Person.lastName, Leader.title
            FROM Leader
            JOIN Person ON Leader.leaderID = Person.id
            ORDER BY Person.lastName, Person.firstName;
        """

        cursor.execute(query)
        leaders = cursor.fetchall()
        return leaders

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/leaders/search", response_model=list[LeaderOutput])
def search_leaders_by_name(name: str):
    """
    Search for leaders by first or last name (partial, case-insensitive match)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT l.leaderID, p.firstName, p.lastName, l.title
            FROM Leader l
            JOIN Person p ON l.leaderID = p.id
            WHERE LOWER(p.firstName) LIKE LOWER(%s)
               OR LOWER(p.lastName) LIKE LOWER(%s)
            ORDER BY p.lastName, p.firstName;
        """

        wildcard = f"%{name}%"
        cursor.execute(query, (wildcard, wildcard))

        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/leaders/{leader_id}", response_model=LeaderOutput)
def get_leader_by_id(leader_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT leaderID, firstName, lastName, title
            FROM Leader
            JOIN Person ON leaderID = id
            WHERE leaderID = %s;
        """, (leader_id,))
        leader = cursor.fetchone()
        if not leader:
            raise HTTPException(404, "Leader not found")
        return leader
    finally:
        cursor.close()
        cnx.close()

@app.get("/leaders/{leader_id}/tasks")
def get_leader_tasks(leader_id: int):
    """
    Returns all tasks a leader is assigned, across all events.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                sc.ID AS shiftID,
                e.ID AS eventID,
                e.Name AS eventName,
                e.StartDateTime,
                e.EndDateTime,
                t.ID AS taskID,
                t.Description AS taskDescription,
                l.Title AS leaderTitle
            FROM ShiftCalender sc
            JOIN Event e ON e.ID = sc.EventID
            JOIN Task t ON t.ID = sc.TaskID
            JOIN Leader l ON l.LeaderID = sc.LeaderID
            WHERE sc.LeaderID = %s;
        """, (leader_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        cnx.close()


@app.post("/event-types", status_code=201)
def create_new_event_type(event_type_data: EventTypeCreate):
    """
    Creates a new event type with custom fields.
    - Stores event type name in MySQL
    - Stores custom field definitions in MongoDB
    """

    # --- VALIDATION ---
    if not event_type_data.custom_fields:
        raise HTTPException(
            status_code=400,
            detail="You must provide at least one custom field."
        )

    # --- INSERT INTO MYSQL ---
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        insert_query = "INSERT INTO EventType (name) VALUES (%s);"
        cursor.execute(insert_query, (event_type_data.name,))
        cnx.commit()

        event_type_id = cursor.lastrowid  # auto-generated ID from MySQL

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")

    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- INSERT CUSTOM FIELDS INTO MONGO ---
    try:
        mongo_collection = mongoDBclient["FP_YG_app"]["eventTypes"]

        mongo_doc = {
            "typeId": event_type_id,
            "name": event_type_data.name,
            "custom_fields": [
                {"field_name": f.field_name, "data_type": f.data_type}
                for f in event_type_data.custom_fields
            ]
        }

        mongo_collection.insert_one(mongo_doc)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

    # --- RESPONSE ---
    return {
        "message": "Event type created successfully",
        "event_type_id": event_type_id,
        "name": event_type_data.name,
        "custom_fields_count": len(event_type_data.custom_fields)
    }


@app.get("/event-types", response_model=list[EventTypeResponse])
def get_all_event_types():
    """
    Retrieves all event types with their custom field schemas from MongoDB.
    """
    try:
        mongo_collection = mongoDBclient["FP_YG_app"]["eventTypes"]
        event_types = list(mongo_collection.find({}))

        result = []
        for et in event_types:
            result.append(EventTypeResponse(
                event_type_id=et["typeId"],
                name=et["name"],
                custom_fields=[
                    CustomFieldDefinition(
                        field_name=f["field_name"],
                        data_type=f["data_type"]
                    )
                    for f in et.get("custom_fields", [])
                ]
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.get("/event-types/{type_id}", response_model=EventTypeResponse)
def get_event_type_by_id(type_id: int):
    """
    Retrieves a specific event type schema by ID from MongoDB.
    """
    try:
        mongo_collection = mongoDBclient["FP_YG_app"]["eventTypes"]
        event_type = mongo_collection.find_one({"typeId": type_id})

        if not event_type:
            raise HTTPException(status_code=404, detail="Event type not found")

        return EventTypeResponse(
            event_type_id=event_type["typeId"],
            name=event_type["name"],
            custom_fields=[
                CustomFieldDefinition(
                    field_name=f["field_name"],
                    data_type=f["data_type"]
                )
                for f in event_type.get("custom_fields", [])
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.get("/event-types/{type_id}/checked-in")
def get_checked_in_for_event_type(type_id: int):
    """
    Returns all checked-in students for all events of a given event type.
    Uses:
    - MySQL to get events & student base info
    - Redis to detect live check-ins
    - MongoDB to enrich event data with custom fields
    """

    # ---------- 1) MYSQL: Get all events of this type ----------
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name
            FROM Event
            WHERE TypeID = %s;
        """, (type_id,))
        events = cursor.fetchall()

        if not events:
            raise HTTPException(status_code=404, detail="No events found for this event type")

        event_ids = [e["id"] for e in events]

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

    # ---------- 2) REDIS: Find checked-in students per event ----------
    if redisClient is None:
        raise HTTPException(status_code=503, detail="Redis not available")

    checked_in_map = {}  # event_id -> set(student_ids)
    check_in_times_map = {}  # event_id -> {student_id: time}

    try:
        for event_id in event_ids:
            set_key = f"event:{event_id}:checkedIn"
            time_key = f"event:{event_id}:checkInTimes"

            student_ids = redisClient.smembers(set_key)
            times = redisClient.hgetall(time_key)

            checked_in_map[event_id] = {int(s) for s in student_ids} if student_ids else set()
            check_in_times_map[event_id] = times

    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")

    # Flatten all student IDs from all events
    all_checked_in_ids = set().union(*checked_in_map.values())

    # ---------- 3) MYSQL: Fetch student details ----------
    student_details = {}
    if all_checked_in_ids:
        try:
            cnx = db_pool.get_connection()
            cursor = cnx.cursor(dictionary=True)

            format_strings = ",".join(["%s"] * len(all_checked_in_ids))
            cursor.execute(f"""
                SELECT p.id, p.firstName, p.lastName, s.grade
                FROM Person p
                JOIN Student s ON s.studentID = p.id
                WHERE p.id IN ({format_strings});
            """, tuple(all_checked_in_ids))

            for row in cursor.fetchall():
                student_details[row["id"]] = row

        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
        finally:
            if cursor: cursor.close()
            if cnx and cnx.is_connected(): cnx.close()

    # ---------- 4) MONGODB: Fetch event custom data ----------
    try:
        mongo_collection = mongoDBclient["FP_YG_app"]["eventCustomData"]
        mongo_docs = list(mongo_collection.find(
            {"eventId": {"$in": event_ids}},
            {"_id": 0}
        ))

        custom_by_event = {doc["eventId"]: doc.get("custom_field_values") for doc in mongo_docs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

    # ---------- 5) Build final combined response ----------
    result = []

    for event in events:
        event_id = event["id"]

        event_entry = {
            "event_id": event_id,
            "event_name": event["name"],
            "custom_fields": custom_by_event.get(event_id),
            "checked_in_students": []
        }

        for student_id in checked_in_map[event_id]:
            event_entry["checked_in_students"].append({
                "student_id": student_id,
                "name": f"{student_details[student_id]['firstName']} {student_details[student_id]['lastName']}",
                "grade": student_details[student_id]["grade"],
                "check_in_time": check_in_times_map[event_id].get(str(student_id))
            })

        result.append(event_entry)

    return {
        "event_type_id": type_id,
        "event_count": len(events),
        "total_checked_in": len(all_checked_in_ids),
        "events": result
    }


@app.post("/events", status_code=201)
def create_event_with_custom_data(event_data: EventCreate):
    """
    Creates a new event with custom field values.
    - Stores base event in MySQL
    - Stores custom field values in MongoDB
    """
    # --- VALIDATE EVENT TYPE EXISTS ---
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id FROM EventType WHERE id = %s;", (event_data.event_type_id,))
        event_type = cursor.fetchone()
        if not event_type:
            raise HTTPException(status_code=404, detail="Event type not found")

        # Validate place exists
        cursor.execute("SELECT id FROM Place WHERE id = %s;", (event_data.place_id,))
        place = cursor.fetchone()
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")

        # Insert event into MySQL
        insert_query = """
                       INSERT INTO Event (name, eventTypeID, placeID, startDateTime, endDateTime)
                       VALUES (%s, %s, %s, %s, %s); \
                       """
        cursor.execute(
            insert_query,
            (
                event_data.name,
                event_data.event_type_id,
                event_data.place_id,
                event_data.start_date_time,
                event_data.end_date_time
            )
        )
        cnx.commit()
        event_id = cursor.lastrowid
        cursor.close()
        cnx.close()

    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- STORE CUSTOM FIELD VALUES IN MONGO (if provided) ---
    if event_data.custom_field_values:
        try:
            # First, get the event type schema to validate fields
            mongo_schema_collection = mongoDBclient["FP_YG_app"]["eventTypes"]
            event_type_schema = mongo_schema_collection.find_one({"typeId": event_data.event_type_id})

            if not event_type_schema:
                raise HTTPException(status_code=404, detail="Event type schema not found in MongoDB")

            # Validate custom fields match schema
            schema_fields = {f["field_name"]: f["data_type"] for f in event_type_schema.get("custom_fields", [])}
            for field_name, field_value in event_data.custom_field_values.items():
                if field_name not in schema_fields:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Custom field '{field_name}' is not defined in event type schema"
                    )

            # Store custom field values
            mongo_data_collection = mongoDBclient["FP_YG_app"]["eventCustomData"]
            mongo_doc = {
                "eventId": event_id,
                "typeId": event_data.event_type_id,
                "custom_field_values": event_data.custom_field_values
            }
            mongo_data_collection.insert_one(mongo_doc)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

    return {
        "message": "Event created successfully",
        "event_id": event_id,
        "name": event_data.name,
        "has_custom_data": event_data.custom_field_values is not None
    }


@app.get("/events/{event_id}", response_model=EventWithCustomData)
def get_event_with_custom_data(event_id: int):
    """
    Retrieves an event with its custom field values from both MySQL and MongoDB.
    """
    # --- GET BASE EVENT FROM MYSQL ---
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
                SELECT id, name, eventTypeID, placeID, startDateTime, endDateTime
                FROM Event \
                WHERE id = %s; \
                """
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.close()
        cnx.close()
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- GET CUSTOM FIELD VALUES FROM MONGO ---
    custom_field_values = None
    try:
        mongo_collection = mongoDBclient["FP_YG_app"]["eventCustomData"]
        custom_data = mongo_collection.find_one({"eventId": event_id})
        if custom_data:
            custom_field_values = custom_data.get("custom_field_values")
    except Exception as e:
        # Don't fail if MongoDB lookup fails, just return None for custom data
        pass

    # Format datetime for response
    start_dt = event["StartDateTime"].isoformat() if event["StartDateTime"] else None
    end_dt = event["EndDateTime"].isoformat() if event["EndDateTime"] else None

    return EventWithCustomData(
        id=event["id"],
        name=event["Name"],
        event_type_id=event["EventTypeID"],
        place_id=event["PlaceID"],
        start_date_time=start_dt,
        end_date_time=end_dt,
        custom_field_values=custom_field_values
    )


@app.put("/events/{event_id}/custom-data", status_code=200)
def update_event_custom_data(event_id: int, custom_data_update: EventCustomDataUpdate):
    """
    Updates the custom field values for an existing event.
    - Validates event exists
    - Validates custom fields match the event type schema
    - Updates or creates custom field values in MongoDB
    """
    # --- VALIDATE EVENT EXISTS AND GET EVENT TYPE ---
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
                SELECT id, Name, EventTypeID
                FROM Event \
                WHERE id = %s; \
                """
        cursor.execute(query, (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        event_type_id = event["EventTypeID"]
        cursor.close()
        cnx.close()
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- VALIDATE CUSTOM FIELDS MATCH EVENT TYPE SCHEMA ---
    try:
        mongo_schema_collection = mongoDBclient["FP_YG_app"]["eventTypes"]
        event_type_schema = mongo_schema_collection.find_one({"typeId": event_type_id})

        if not event_type_schema:
            raise HTTPException(
                status_code=404,
                detail=f"Event type schema not found for event type ID {event_type_id}"
            )

        # Validate custom fields match schema
        schema_fields = {f["field_name"]: f["data_type"] for f in event_type_schema.get("custom_fields", [])}

        if not schema_fields:
            raise HTTPException(
                status_code=400,
                detail="This event type does not have any custom fields defined"
            )

        # Validate all provided fields exist in schema
        for field_name, field_value in custom_data_update.custom_field_values.items():
            if field_name not in schema_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Custom field '{field_name}' is not defined in event type schema. "
                           f"Valid fields: {list(schema_fields.keys())}"
                )

            # Basic type validation
            expected_type = schema_fields[field_name]
            if expected_type == "boolean" and not isinstance(field_value, bool):
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field_name}' must be a boolean, got {type(field_value).__name__}"
                )
            elif expected_type == "number" and not isinstance(field_value, (int, float)):
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field_name}' must be a number, got {type(field_value).__name__}"
                )
            elif expected_type == "text" and not isinstance(field_value, str):
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field_name}' must be text (string), got {type(field_value).__name__}"
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB validation error: {e}")

    # --- UPDATE OR CREATE CUSTOM DATA IN MONGO ---
    try:
        mongo_data_collection = mongoDBclient["FP_YG_app"]["eventCustomData"]

        # Check if custom data already exists
        existing_data = mongo_data_collection.find_one({"eventId": event_id})

        if existing_data:
            # Update existing document
            mongo_data_collection.update_one(
                {"eventId": event_id},
                {"$set": {"custom_field_values": custom_data_update.custom_field_values}}
            )
            action = "updated"
        else:
            # Create new document
            mongo_doc = {
                "eventId": event_id,
                "typeId": event_type_id,
                "custom_field_values": custom_data_update.custom_field_values
            }
            mongo_data_collection.insert_one(mongo_doc)
            action = "created"

        return {
            "message": f"Event custom data {action} successfully",
            "event_id": event_id,
            "event_name": event["Name"],
            "event_type_id": event_type_id,
            "custom_field_values": custom_data_update.custom_field_values,
            "action": action
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")




# ========== REDIS CHECK-IN ENDPOINTS ==========

@app.get("/redis/test")
def test_redis_connection():
    """
    Diagnostic endpoint to test Redis connection and basic operations.
    """
    if redisClient is None:
        return {
            "status": "error",
            "message": "Redis client is None - connection failed at startup",
            "connected": False
        }

    try:
        # Test basic operations
        test_key = "test:connection"
        test_value = "test_value"

        # Test SET/GET
        redisClient.set(test_key, test_value, ex=10)  # Expires in 10 seconds
        retrieved = redisClient.get(test_key)

        # Test SET operations
        test_set_key = "test:set"
        redisClient.sadd(test_set_key, "member1")
        redisClient.sadd(test_set_key, "member2")
        set_members = redisClient.smembers(test_set_key)
        set_count = redisClient.scard(test_set_key)

        # Cleanup
        redisClient.delete(test_key)
        redisClient.delete(test_set_key)

        return {
            "status": "success",
            "message": "Redis connection and operations working correctly",
            "connected": True,
            "tests": {
                "set_get": retrieved == test_value,
                "set_operations": len(set_members) == 2 and set_count == 2,
                "ping": redisClient.ping()
            }
        }
    except redis.ConnectionError as e:
        return {
            "status": "error",
            "message": f"Redis connection error: {e}",
            "connected": False,
            "error_type": "ConnectionError"
        }
    except redis.RedisError as e:
        return {
            "status": "error",
            "message": f"Redis error: {e}",
            "connected": True,
            "error_type": "RedisError"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {type(e).__name__}: {e}",
            "connected": None,
            "error_type": type(e).__name__
        }


@app.post("/events/{event_id}/check-in/{student_id}", status_code=200)
def check_in_student(event_id: int, student_id: int):
    """
    Checks a student into an event using Redis.
    - Adds student to Redis set for real-time tracking
    - Records check-in timestamp
    """
    # --- VALIDATE EVENT EXISTS ---
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Validate student exists and is registered for event
        cursor.execute("""
                       SELECT r.ID
                       FROM Registration r
                       WHERE r.StudentID = %s
                         AND r.EventID = %s;
                       """, (student_id, event_id))
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(
                status_code=404,
                detail="Student not registered for this event"
            )
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- ADD TO REDIS SET ---
    if redisClient is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        check_in_times_key = f"event:{event_id}:checkInTimes"

        # Check if already checked in
        if redisClient.sismember(checked_in_key, str(student_id)):
            return {
                "message": "Student already checked in",
                "event_id": event_id,
                "student_id": student_id,
                "already_checked_in": True
            }

        # Add to set
        redisClient.sadd(checked_in_key, str(student_id))

        # Record check-in time
        timestamp = datetime.now().isoformat()
        redisClient.hset(check_in_times_key, str(student_id), timestamp)

        # Get current count
        count = redisClient.scard(checked_in_key)

        return {
            "message": "Student checked in successfully",
            "event_id": event_id,
            "student_id": student_id,
            "check_in_time": timestamp,
            "current_count": count
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}")


@app.post("/events/{event_id}/check-out/{student_id}", status_code=200)
def check_out_student(event_id: int, student_id: int):
    """
    Checks a student out of an event using Redis.
    - Removes student from Redis set
    - Records check-out timestamp
    """
    # --- VALIDATE EVENT EXISTS ---
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- REMOVE FROM REDIS SET ---
    if redisClient is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        check_out_times_key = f"event:{event_id}:checkOutTimes"

        # Check if checked in
        if not redisClient.sismember(checked_in_key, str(student_id)):
            return {
                "message": "Student not currently checked in",
                "event_id": event_id,
                "student_id": student_id,
                "was_checked_in": False
            }

        # Remove from set
        redisClient.srem(checked_in_key, str(student_id))

        # Record check-out time
        timestamp = datetime.now().isoformat()
        redisClient.hset(check_out_times_key, str(student_id), timestamp)

        # Get current count
        count = redisClient.scard(checked_in_key)

        return {
            "message": "Student checked out successfully",
            "event_id": event_id,
            "student_id": student_id,
            "check_out_time": timestamp,
            "current_count": count
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}")


@app.get("/events/{event_id}/checked-in")
def get_checked_in_students(event_id: int):
    """
    Gets all students currently checked in to an event from Redis.
    Returns list of student IDs and their check-in times.
    """
    try:
        # --- VALIDATE EVENT EXISTS ---
        logger.info(f"Getting checked-in students for event {event_id}")
        cnx = None
        cursor = None
        try:
            cnx = db_pool.get_connection()
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("SELECT ID, Name FROM Event WHERE ID = %s;", (event_id,))
            event = cursor.fetchone()
            if not event:
                logger.warning(f"Event {event_id} not found")
                raise HTTPException(status_code=404, detail="Event not found")
            event_name = event.get("Name") or event.get("name") or "Unknown"
            logger.info(f"Event found: {event_name}")
        except HTTPException:
            raise
        except mysql.connector.Error as err:
            logger.error(f"MySQL error: {err}")
            raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
        finally:
            if cursor:
                cursor.close()
            if cnx and cnx.is_connected():
                cnx.close()

        # --- GET FROM REDIS ---
        if redisClient is None:
            logger.error("Redis client is None")
            raise HTTPException(status_code=503, detail="Redis connection not available")

        logger.info("Accessing Redis for checked-in students")
        checked_in_key = f"event:{event_id}:checkedIn"
        check_in_times_key = f"event:{event_id}:checkInTimes"

        # Get all checked-in student IDs (returns a set)
        student_ids = redisClient.smembers(checked_in_key)
        logger.info(f"Found {len(student_ids) if student_ids else 0} checked-in students")

        # Handle case where set might be None or empty
        if student_ids is None:
            student_ids = set()

        # Get check-in times for each student
        checked_in_list = []
        for student_id in student_ids:
            try:
                # Convert to int for response
                student_id_int = int(student_id)
                # Get check-in time from hash (may be None if not set)
                check_in_time = redisClient.hget(check_in_times_key, student_id)
                checked_in_list.append({
                    "student_id": student_id_int,
                    "check_in_time": check_in_time
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid student_id format: {student_id}, error: {e}")
                # Skip invalid student IDs
                continue

        result = {
            "event_id": event_id,
            "event_name": event_name,
            "checked_in_students": checked_in_list,
            "count": len(checked_in_list)
        }
        logger.info(f"Returning result with {len(checked_in_list)} students")
        return result

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    except KeyError as e:
        logger.error(f"Missing key in event data: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Missing key in event data: {str(e)}")
    except Exception as e:
        # Log full traceback for debugging
        logger.error(f"Unexpected error in get_checked_in_students: {type(e).__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {type(e).__name__}: {str(e)}"
        )


@app.get("/events/{event_id}/check-in-count")
def get_check_in_count(event_id: int):
    """
    Gets the current count of students checked in to an event from Redis.
    """
    # --- VALIDATE EVENT EXISTS ---
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID, Name FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.close()
        cnx.close()
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- GET COUNT FROM REDIS ---
    if redisClient is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        count = redisClient.scard(checked_in_key)

        return {
            "event_id": event_id,
            "event_name": event["Name"],
            "checked_in_count": count
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}")


@app.post("/events/{event_id}/finalize", status_code=200)
def finalize_event_check_ins(event_id: int):
    """
    Finalizes an event by persisting Redis check-ins to MySQL and cleaning up Redis keys.
    - Reads all checked-in students from Redis
    - Creates/updates Attendee records in MySQL
    - Cleans up Redis keys for the event
    """
    # --- VALIDATE EVENT EXISTS ---
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID, Name FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        event_name = event.get("Name") or event.get("name") or "Unknown"
    except HTTPException:
        raise
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # --- GET CHECKED-IN STUDENTS FROM REDIS ---
    if redisClient is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        check_in_times_key = f"event:{event_id}:checkInTimes"
        check_out_times_key = f"event:{event_id}:checkOutTimes"

        student_ids = redisClient.smembers(checked_in_key)

        if not student_ids:
            # No one checked in, just clean up Redis keys
            redisClient.delete(checked_in_key)
            redisClient.delete(check_in_times_key)
            redisClient.delete(check_out_times_key)
            return {
                "message": "Event finalized - no check-ins to persist",
                "event_id": event_id,
                "students_persisted": 0
            }

        # --- PERSIST TO MYSQL ---
        cnx = None
        cursor = None
        try:
            cnx = db_pool.get_connection()
            cursor = cnx.cursor()

            persisted_count = 0
            for student_id_str in student_ids:
                student_id = int(student_id_str)

                # Get registration ID for this student and event
                cursor.execute("""
                               SELECT r.ID
                               FROM Registration r
                               WHERE r.StudentID = %s
                                 AND r.EventID = %s;
                               """, (student_id, event_id))
                registration = cursor.fetchone()

                if registration:
                    registration_id = registration[0]

                    # Get check-in and check-out times from Redis
                    check_in_time_str = redisClient.hget(check_in_times_key, student_id_str)
                    check_out_time_str = redisClient.hget(check_out_times_key, student_id_str)

                    # Convert ISO timestamps to TIME format (HH:MM:SS)
                    check_in_time = None
                    check_out_time = None

                    if check_in_time_str:
                        # Parse ISO format and extract time
                        dt = datetime.fromisoformat(check_in_time_str)
                        check_in_time = dt.strftime("%H:%M:%S")

                    if check_out_time_str:
                        dt = datetime.fromisoformat(check_out_time_str)
                        check_out_time = dt.strftime("%H:%M:%S")

                    # Check if Attendee record already exists
                    cursor.execute("""
                                   SELECT RegistrationID
                                   FROM Attendee
                                   WHERE RegistrationID = %s;
                                   """, (registration_id,))
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing record
                        cursor.execute("""
                                       UPDATE Attendee
                                       SET CheckInTime  = %s,
                                           CheckOutTime = %s
                                       WHERE RegistrationID = %s;
                                       """, (check_in_time, check_out_time, registration_id))
                    else:
                        # Insert new record
                        cursor.execute("""
                                       INSERT INTO Attendee (RegistrationID, CheckInTime, CheckOutTime)
                                       VALUES (%s, %s, %s);
                                       """, (registration_id, check_in_time, check_out_time))

                    persisted_count += 1

            cnx.commit()

            # --- CLEAN UP REDIS KEYS ---
            redisClient.delete(checked_in_key)
            redisClient.delete(check_in_times_key)
            redisClient.delete(check_out_times_key)

            return {
                "message": "Event finalized successfully",
                "event_id": event_id,
                "students_persisted": persisted_count,
                "redis_keys_cleaned": True
            }

        except HTTPException:
            raise
        except mysql.connector.Error as err:
            if cnx:
                cnx.rollback()
            raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Redis error: {e}")
        except Exception as e:
            if cnx:
                cnx.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {type(e).__name__}: {e}")
        finally:
            if cursor:
                cursor.close()
            if cnx and cnx.is_connected():
                cnx.close()
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error in finalize: {type(e).__name__}: {e}")


@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")

