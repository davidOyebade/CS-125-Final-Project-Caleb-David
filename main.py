#Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
# Caleb Song & David Oyebade

import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os

from mongodb_implement import get_mongo_client, get_mongo_db
from redis_implement import get_redis_client, get_redis_conn

# --- Database Configuration ---
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "127.0.0.1"
DB_NAME = "FP_YG_app"

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
get_mongo_client()
get_redis_client()

# --- FastAPI App ---
app = FastAPI(
    title="Youth Group API",
    description="An API for interacting with the FP_YG_app database.",
    version="1.0.0"
)

# --- Pydantic Models (for request/response validation) ---
class Person(BaseModel):
    id: int
    firstName: str
    lastName: str

class Event(BaseModel):
    id: int
    Name: str

class SmallGroup(BaseModel):
    id: int
    Name: str
class Student(BaseModel):
    id: int
    FirstName: str
    LastName: str
    Grade: int
class Parent(BaseModel):
    ParentID: int
    FirstName: str
    LastName: str

class VolunteerOutput(BaseModel):
    VolunteerID: int
    FirstName: str
    LastName: str

class LeaderOutput(BaseModel):
    LeaderID: int
    FirstName: str
    LastName: str
    Title: str | None = None

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

@app.get("/students", response_model=list[Student])
def get_all_students():
    """
    Retrieves a list of all students
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, FirstName, LastName, Grade FROM Person JOIN Student ON Student.StudentID = Person.id  ORDER BY lastName, firstName;")
        students = cursor.fetchall()
        return students
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()
@app.get("/students/{student_grade}", response_model=list[Student])
def get_students_by_grade(student_grade: int):
    """
    Retrieve students by grade
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, FirstName, LastName, Grade FROM Person JOIN Student ON Student.StudentID = Person.id WHERE Grade = %s ORDER BY lastName, firstName;"
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
@app.get("/student/{student_id}", response_model=Student)
def get_student_by_id(student_id: int):
    """
    Retrieves a specific student by their ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Use parameterized query to prevent SQL injection
        query = "SELECT id, firstName, lastName, Grade FROM Person JOIN Student ON Student.StudentID = Person.id WHERE id = %s;"
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


@app.get("/events", response_model=list[Event])
def get_all_events():
    """
    Retrieves a list of all products.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, Name FROM Event ORDER BY Name;")
        events = cursor.fetchall()
        return events
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
        query = "SELECT id, Name FROM Event WHERE id = %s;"
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


@app.get("/smallgroups", response_model=list[SmallGroup])
def get_all_smallgroups():
    """
    Retrieves a list of all products.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, Name FROM SmallGroup ORDER BY Name;")
        smallgroups = cursor.fetchall()
        return smallgroups
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
        query = "SELECT id, Name FROM SmallGroup WHERE id = %s;"
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

@app.get("/parents", response_model=list[Parent])
def get_all_parents():
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT Parent.ParentID, FirstName, LastName
            FROM Parent 
            JOIN Person ON Parent.ParentID = Person.ID;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/parents/{parent_id}", response_model=Parent)
def get_parent_by_id(parent_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT ParentID, FirstName, LastName
            FROM Parent JOIN Person ON ParentID = ID
            WHERE ParentID = %s;
        """
        cursor.execute(query, (parent_id,))
        parent = cursor.fetchone()
        if not parent:
            raise HTTPException(404, "Parent not found")
        return parent
    finally:
        cursor.close()
        cnx.close()

@app.get("/parent/search", response_model=list[Parent])
def search_parents_by_name(name: str):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        like = f"%{name}%"
        query = """
            SELECT ParentID, FirstName, LastName
            FROM Parent JOIN Person ON ParentID = ID
            WHERE FirstName LIKE %s OR LastName LIKE %s;
        """
        cursor.execute(query, (like, like))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/students/{student_id}/parents", response_model=list[Parent])
def get_parents_of_student(student_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT Parent.ParentID AS ParentID, FirstName, LastName
            FROM StudentParent
            JOIN Parent ON Parent.ParentID = StudentParent.ParentID
            JOIN Person ON Parent.ParentID = Person.ID
            WHERE StudentParent.StudentID = %s;
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/people/search", response_model=list[Person])
def search_people_by_name(name: str):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        like = f"%{name}%"
        query = """
            SELECT ID AS id, FirstName, LastName
            FROM Person
            WHERE FirstName LIKE %s OR LastName LIKE %s;
        """
        cursor.execute(query, (like, like))
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
            "INSERT INTO PersonGroup(PersonID, SmallGroupID) VALUES (%s, %s);",
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
            "DELETE FROM PersonGroup WHERE PersonID = %s AND SmallGroupID = %s;",
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
            SELECT VolunteerID, FirstName, LastName
            FROM Volunteer JOIN Person ON VolunteerID = ID;
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/events/{event_id}/roster")
def get_event_roster(event_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT Registration.ID AS RegistrationID, Student.StudentID, FirstName, LastName
            FROM Registration
            JOIN Student ON Registration.StudentID = Student.StudentID
            JOIN Person ON Student.StudentID = Person.ID
            WHERE EventID = %s;
        """
        cursor.execute(query, (event_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/people/{person_id}/smallgroups")
def get_smallgroups_for_person(person_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT SmallGroup.ID, SmallGroup.Name
            FROM PersonGroup
            JOIN SmallGroup ON PersonGroup.SmallGroupID = SmallGroup.ID
            WHERE PersonID = %s;
        """
        cursor.execute(query, (person_id,))
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
            SELECT Leader.LeaderID, Person.FirstName, Person.LastName, Leader.Title
            FROM Leader
            JOIN Person ON Leader.LeaderID = Person.ID
            ORDER BY Person.LastName, Person.FirstName;
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

@app.get("/leaders/{leader_id}", response_model=LeaderOutput)
def get_leader_by_id(leader_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT LeaderID, FirstName, LastName, Title
            FROM Leader
            JOIN Person ON LeaderID = ID
            WHERE LeaderID = %s;
        """, (leader_id,))
        leader = cursor.fetchone()
        if not leader:
            raise HTTPException(404, "Leader not found")
        return leader
    finally:
        cursor.close()
        cnx.close()

@app.get("/leader/search", response_model=list[LeaderOutput])
def search_leaders(name: str):
    try:
        like = f"%{name}%"
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT LeaderID, FirstName, LastName, Title
            FROM Leader
            JOIN Person ON LeaderID = ID
            WHERE FirstName LIKE %s OR LastName LIKE %s;
        """, (like, like))

        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()

@app.get("/smallgroups/{group_id}/roster")
def get_small_group_roster(group_id: int):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT Person.ID, FirstName, LastName
            FROM PersonGroup
            JOIN Person ON PersonGroup.PersonID = Person.ID
            WHERE SmallGroupID = %s
            ORDER BY LastName, FirstName;
        """, (group_id,))

        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()




@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")


if __name__ == "__main__":
    print("\nTo run this FastAPI application:")
    print("1. Make sure you have installed the required packages: pip install -r requirements.txt")
    print("2. Run the server: uvicorn demo3_fastapi_app:app --reload --port 8000")
    print("3. Open your browser and go to http://127.0.0.1:8000/docs for the API documentation.")
    print("4. Open your browser and go to http://127.0.0.1:8000/demo for a UI demo.")

