
import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os

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

