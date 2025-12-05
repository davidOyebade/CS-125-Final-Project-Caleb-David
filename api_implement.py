
import mysql.connector
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import redis
from datetime import datetime
from typing import Optional, Dict, Any
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Database Configuration ---
DB_USER = "root"
DB_PASSWORD = "password"
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

# Mongo DB Connection
uri = "mongodb+srv://user:password@rushhourcluster1.5psh0lb.mongodb.net/?appName=RushHourCluster1"
mongoDBclient = MongoClient(uri, server_api=ServerApi('1'))
try:
    mongoDBclient.admin.command('ping')
    print("MongoDB connection created successfully!")
except Exception as e:
    print(f"Error creating connection: {e}")

# Redis Connection
try:
    redisClient = redis.Redis(
        host='redis-16262.c289.us-west-1-2.ec2.cloud.redislabs.com',
        port=16262,
        decode_responses=True,
        username="default",
        password="password",
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test connection with ping
    redisClient.ping()
    print("✓ Redis connection created successfully!")
except redis.ConnectionError as e:
    print(f"✗ Redis connection error: {e}")
    print("  Redis endpoints will not work until connection is fixed.")
    redisClient = None
except Exception as e:
    print(f"✗ Error creating Redis connection: {e}")
    redisClient = None

# --- FastAPI App ---
app = FastAPI(
    title="Youth Group API",
    description="An API for interacting with the FP_YG_app database.",
    version="1.0.0"
)

# Global exception handler to catch unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {type(exc).__name__}: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {type(exc).__name__}: {str(exc)}",
            "error_type": type(exc).__name__,
            "path": str(request.url.path)
        }
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

# Defines a single custom field for an event type
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
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
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
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
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
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
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
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
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
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
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
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")


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

        insert_query = "INSERT INTO EventType (Name) VALUES (%s);"
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
        cursor.execute("SELECT ID FROM EventType WHERE ID = %s;", (event_data.event_type_id,))
        event_type = cursor.fetchone()
        if not event_type:
            raise HTTPException(status_code=404, detail="Event type not found")
        
        # Validate place exists
        cursor.execute("SELECT ID FROM Place WHERE ID = %s;", (event_data.place_id,))
        place = cursor.fetchone()
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
        
        # Insert event into MySQL
        insert_query = """
            INSERT INTO Event (Name, EventTypeID, PlaceID, StartDateTime, EndDateTime)
            VALUES (%s, %s, %s, %s, %s);
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
            SELECT id, Name, EventTypeID, PlaceID, StartDateTime, EndDateTime
            FROM Event WHERE id = %s;
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
            FROM Event WHERE id = %s;
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
            WHERE r.StudentID = %s AND r.EventID = %s;
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
                    WHERE r.StudentID = %s AND r.EventID = %s;
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
                            SET CheckInTime = %s, CheckOutTime = %s
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


if __name__ == "__main__":
    print("\nTo run this FastAPI application:")
    print("1. Make sure you have installed the required packages: pip install -r requirements.txt")
    print("2. Run the server: uvicorn demo3_fastapi_app:app --reload --port 8000")
    print("3. Open your browser and go to http://127.0.0.1:8000/docs for the API documentation.")
    print("4. Open your browser and go to http://127.0.0.1:8000/ for a UI demo.")

