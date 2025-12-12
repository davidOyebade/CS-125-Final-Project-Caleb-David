# Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
# Caleb Song & David Oyebade

"""
GraphQL Schema for Youth Group Management System API

This file defines the GraphQL schema for our Youth Group Management System.

What is GraphQL?
GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data.
It gives clients the power to ask for exactly what they need and nothing more, makes it easier to evolve APIs over time,
and enables powerful developer tools.

Key Concepts:
1. Schema: The backbone of a GraphQL API. It defines the types of data that can be queried.
2. Types: The building blocks of a GraphQL schema. Each type has one or more fields.
3. Query: A type that defines all the read operations a client can perform.
4. Mutation: A type that defines all the write operations (create, update, delete).
5. Resolver: A function that "resolves" a value for a field in a query or mutation.
"""

import strawberry
from strawberry.scalars import JSON
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

# Database connections will be set at runtime to avoid circular imports
# These will be initialized in graphql_app.py
db_pool = None
redisClient = None
mongoDBclient = None


def set_database_connections(db_pool_conn, redis_conn, mongo_conn):
    """Set database connections at runtime to avoid circular imports."""
    global db_pool, redisClient, mongoDBclient
    db_pool = db_pool_conn
    redisClient = redis_conn;
    mongoDBclient = mongo_conn


# --- Strawberry Types ---

@strawberry.type
class Person:
    """GraphQL type representing a person."""
    id: int
    firstName: str
    lastName: str


@strawberry.type
class Event:
    """GraphQL type representing an event (basic)."""
    id: int
    name: str


@strawberry.type
class SmallGroup:
    """GraphQL type representing a small group."""
    id: int
    name: str


@strawberry.type
class CustomFieldDefinition:
    """GraphQL type for a custom field definition in an event type."""
    field_name: str
    data_type: str


@strawberry.type
class EventType:
    """GraphQL type for an event type with its custom field schema."""
    event_type_id: int
    name: str
    custom_fields: List[CustomFieldDefinition]


@strawberry.type
class EventWithCustomData:
    """GraphQL type for an event with its custom field values from MongoDB."""
    id: int
    name: str
    event_type_id: int
    place_id: int
    checked_in: int
    start_date_time: Optional[str] = None
    end_date_time: Optional[str] = None
    custom_field_values: Optional[JSON] = None


@strawberry.type
class CheckedInStudent:
    """GraphQL type for a checked-in student."""
    student_id: int
    check_in_time: Optional[str] = None


@strawberry.type
class CheckedInResponse:
    """GraphQL type for the checked-in students response."""
    event_id: int
    event_name: str
    checked_in_students: List[CheckedInStudent]
    count: int


@strawberry.type
class CheckInCount:
    """GraphQL type for check-in count."""
    event_id: int
    event_name: str
    checked_in_count: int


# --- Strawberry Input Types ---

@strawberry.input
class CustomFieldDefinitionInput:
    """Input type for a custom field definition."""
    field_name: str
    data_type: str


@strawberry.input
class EventTypeCreateInput:
    """Input type for creating a new event type."""
    name: str
    custom_fields: List[CustomFieldDefinitionInput]


@strawberry.input
class EventCreateInput:
    """Input type for creating a new event."""
    name: str
    event_type_id: int
    place_id: int
    start_date_time: str
    end_date_time: str
    custom_field_values: Optional[JSON] = None


@strawberry.input
class EventCustomDataUpdateInput:
    """Input type for updating event custom data."""
    custom_field_values: JSON


# --- Helper Functions to Access Database ---
# Use the imported connections from api_implement

def get_db_connection():
    """Get a MySQL database connection from the pool."""
    if db_pool is None:
        raise HTTPException(status_code=500, detail="Database pool not available")
    return db_pool.get_connection()


def get_redis_client():
    """Get Redis client."""
    return redisClient


def get_mongo_client():
    """Get MongoDB client."""
    if mongoDBclient is None:
        raise HTTPException(status_code=500, detail="MongoDB client not available")
    return mongoDBclient


# --- Query Resolvers ---

def get_all_people_resolver() -> List[Person]:
    """Resolver to fetch all people."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, firstName, lastName FROM Person ORDER BY lastName, firstName;")
        people = cursor.fetchall()
        return [Person(id=p["id"], firstName=p["firstName"], lastName=p["lastName"]) for p in people]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_person_by_id_resolver(person_id: int) -> Optional[Person]:
    """Resolver to fetch a person by ID."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, firstName, lastName FROM Person WHERE id = %s;", (person_id,))
        person = cursor.fetchone()
        if not person:
            return None
        return Person(id=person["id"], firstName=person["firstName"], lastName=person["lastName"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_all_events_resolver() -> List[Event]:
    """Resolver to fetch all events (basic info only)."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, Name FROM Event ORDER BY Name;")
        events = cursor.fetchall()
        return [Event(id=e["id"], name=e["Name"]) for e in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_all_events_with_counts_resolver() -> List[EventWithCustomData]:
    """Resolver to fetch all events with their check-in counts from Redis."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
                       SELECT id, Name, EventTypeID, PlaceID, StartDateTime, EndDateTime
                       FROM Event
                       ORDER BY Name;
                       """)
        events = cursor.fetchall()

        result = []
        redis_client = get_redis_client()

        for event in events:
            event_id = event["id"]

            # Get custom field values from MongoDB
            custom_field_values = None
            try:
                mongo_client = get_mongo_client()
                mongo_collection = mongo_client["FP_YG_app"]["eventCustomData"]
                custom_data = mongo_collection.find_one({"eventId": event_id})
                if custom_data:
                    custom_field_values = custom_data.get("custom_field_values")
            except Exception:
                pass

            # Get check-in count from Redis
            checked_in_count = 0
            try:
                if redis_client:
                    checked_in_key = f"event:{event_id}:checkedIn"
                    checked_in_count = redis_client.scard(checked_in_key)
            except Exception:
                pass

            start_dt = event["StartDateTime"].isoformat() if event["StartDateTime"] else None
            end_dt = event["EndDateTime"].isoformat() if event["EndDateTime"] else None

            result.append(EventWithCustomData(
                id=event["id"],
                name=event["Name"],
                event_type_id=event["EventTypeID"],
                place_id=event["PlaceID"],
                checked_in=checked_in_count,
                start_date_time=start_dt,
                end_date_time=end_dt,
                custom_field_values=custom_field_values
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_event_by_id_resolver(event_id: int) -> Optional[EventWithCustomData]:
    """Resolver to fetch an event with custom data and check-in count."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
                       SELECT id, Name, EventTypeID, PlaceID, StartDateTime, EndDateTime
                       FROM Event
                       WHERE id = %s;
                       """, (event_id,))
        event = cursor.fetchone()
        if not event:
            return None

        # Get custom field values from MongoDB
        custom_field_values = None
        try:
            mongo_client = get_mongo_client()
            mongo_collection = mongo_client["FP_YG_app"]["eventCustomData"]
            custom_data = mongo_collection.find_one({"eventId": event_id})
            if custom_data:
                custom_field_values = custom_data.get("custom_field_values")
        except Exception:
            pass  # Don't fail if MongoDB lookup fails

        # Get check-in count from Redis
        checked_in_count = 0
        try:
            redis_client = get_redis_client()
            if redis_client:
                checked_in_key = f"event:{event_id}:checkedIn"
                checked_in_count = redis_client.scard(checked_in_key)
        except Exception:
            pass  # Don't fail if Redis lookup fails

        start_dt = event["StartDateTime"].isoformat() if event["StartDateTime"] else None
        end_dt = event["EndDateTime"].isoformat() if event["EndDateTime"] else None

        return EventWithCustomData(
            id=event["id"],
            name=event["Name"],
            event_type_id=event["EventTypeID"],
            place_id=event["PlaceID"],
            checked_in=checked_in_count,
            start_date_time=start_dt,
            end_date_time=end_dt,
            custom_field_values=custom_field_values
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_all_smallgroups_resolver() -> List[SmallGroup]:
    """Resolver to fetch all small groups."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, Name FROM SmallGroup ORDER BY Name;")
        smallgroups = cursor.fetchall()
        return [SmallGroup(id=sg["id"], name=sg["Name"]) for sg in smallgroups]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_smallgroup_by_id_resolver(smallgroup_id: int) -> Optional[SmallGroup]:
    """Resolver to fetch a small group by ID."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, Name FROM SmallGroup WHERE id = %s;", (smallgroup_id,))
        smallgroup = cursor.fetchone()
        if not smallgroup:
            return None
        return SmallGroup(id=smallgroup["id"], name=smallgroup["Name"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_all_event_types_resolver() -> List[EventType]:
    """Resolver to fetch all event types with their schemas."""
    try:
        mongo_client = get_mongo_client()
        mongo_collection = mongo_client["FP_YG_app"]["eventTypes"]
        event_types = list(mongo_collection.find({}))

        result = []
        for et in event_types:
            result.append(EventType(
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


def get_event_type_by_id_resolver(type_id: int) -> Optional[EventType]:
    """Resolver to fetch an event type by ID."""
    try:
        mongo_client = get_mongo_client()
        mongo_collection = mongo_client["FP_YG_app"]["eventTypes"]
        event_type = mongo_collection.find_one({"typeId": type_id})

        if not event_type:
            return None

        return EventType(
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


def get_checked_in_students_resolver(event_id: int) -> Optional[CheckedInResponse]:
    """Resolver to get all checked-in students for an event."""
    # Validate event exists
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID, Name FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            return None
        event_name = event.get("Name") or event.get("name") or "Unknown"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # Get from Redis
    redis_client = get_redis_client()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        check_in_times_key = f"event:{event_id}:checkInTimes"

        student_ids = redis_client.smembers(checked_in_key)
        if student_ids is None:
            student_ids = set()

        checked_in_list = []
        for student_id in student_ids:
            try:
                student_id_int = int(student_id)
                check_in_time = redis_client.hget(check_in_times_key, student_id)
                checked_in_list.append(CheckedInStudent(
                    student_id=student_id_int,
                    check_in_time=check_in_time
                ))
            except (ValueError, TypeError):
                continue

        return CheckedInResponse(
            event_id=event_id,
            event_name=event_name,
            checked_in_students=checked_in_list,
            count=len(checked_in_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


def get_check_in_count_resolver(event_id: int) -> Optional[CheckInCount]:
    """Resolver to get the check-in count for an event."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID, Name FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            return None
        event_name = event.get("Name") or event.get("name") or "Unknown"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    redis_client = get_redis_client()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        count = redis_client.scard(checked_in_key)

        return CheckInCount(
            event_id=event_id,
            event_name=event_name,
            checked_in_count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


# --- Mutation Resolvers ---

def create_event_type_resolver(event_type_data: EventTypeCreateInput) -> EventType:
    """Resolver to create a new event type."""
    if not event_type_data.custom_fields:
        raise HTTPException(status_code=400, detail="You must provide at least one custom field.")

    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO EventType (Name) VALUES (%s);", (event_type_data.name,))
        cnx.commit()
        event_type_id = cursor.lastrowid
    except Exception as e:
        if cnx:
            cnx.rollback()
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # Store in MongoDB
    try:
        mongo_client = get_mongo_client()
        mongo_collection = mongo_client["FP_YG_app"]["eventTypes"]
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

    return EventType(
        event_type_id=event_type_id,
        name=event_type_data.name,
        custom_fields=[
            CustomFieldDefinition(field_name=f.field_name, data_type=f.data_type)
            for f in event_type_data.custom_fields
        ]
    )


def check_in_student_resolver(event_id: int, student_id: int) -> bool:
    """Resolver to check in a student. Returns true if successful."""
    # Validate event and registration
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        cursor.execute("""
                       SELECT r.ID
                       FROM Registration r
                       WHERE r.StudentID = %s
                         AND r.EventID = %s;
                       """, (student_id, event_id))
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(status_code=404, detail="Student not registered for this event")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    # Add to Redis
    redis_client = get_redis_client()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        check_in_times_key = f"event:{event_id}:checkInTimes"

        if redis_client.sismember(checked_in_key, str(student_id)):
            return True  # Already checked in

        redis_client.sadd(checked_in_key, str(student_id))
        timestamp = datetime.now().isoformat()
        redis_client.hset(check_in_times_key, str(student_id), timestamp)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


def check_out_student_resolver(event_id: int, student_id: int) -> bool:
    """Resolver to check out a student. Returns true if successful."""
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID FROM Event WHERE ID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

    redis_client = get_redis_client()
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis connection not available")

    try:
        checked_in_key = f"event:{event_id}:checkedIn"
        check_out_times_key = f"event:{event_id}:checkOutTimes"

        if not redis_client.sismember(checked_in_key, str(student_id)):
            return False  # Not checked in

        redis_client.srem(checked_in_key, str(student_id))
        timestamp = datetime.now().isoformat()
        redis_client.hset(check_out_times_key, str(student_id), timestamp)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


# --- Query Type ---

@strawberry.type
class Query:
    """Defines all the queries (read operations) available in the Youth Group GraphQL API."""

    people: List[Person] = strawberry.field(
        resolver=get_all_people_resolver,
        description="Retrieves a list of all people from MySQL."
    )

    person: Optional[Person] = strawberry.field(
        resolver=get_person_by_id_resolver,
        description="Retrieves a specific person by their ID from MySQL."
    )

    events: List[Event] = strawberry.field(
        resolver=get_all_events_resolver,
        description="Retrieves a list of all events (basic info only) from MySQL."
    )

    eventsWithCounts: List[EventWithCustomData] = strawberry.field(
        resolver=get_all_events_with_counts_resolver,
        description="Retrieves all events with check-in counts from Redis and custom data from MongoDB."
    )

    event: Optional[EventWithCustomData] = strawberry.field(
        resolver=get_event_by_id_resolver,
        description="Retrieves an event with custom field values from MySQL/MongoDB and check-in count from Redis."
    )

    smallGroups: List[SmallGroup] = strawberry.field(
        resolver=get_all_smallgroups_resolver,
        description="Retrieves a list of all small groups from MySQL."
    )

    smallGroup: Optional[SmallGroup] = strawberry.field(
        resolver=get_smallgroup_by_id_resolver,
        description="Retrieves a specific small group by ID from MySQL."
    )

    eventTypes: List[EventType] = strawberry.field(
        resolver=get_all_event_types_resolver,
        description="Retrieves all event types with their custom field schemas from MongoDB."
    )

    eventType: Optional[EventType] = strawberry.field(
        resolver=get_event_type_by_id_resolver,
        description="Retrieves a specific event type schema by ID from MongoDB."
    )

    checkedInStudents: Optional[CheckedInResponse] = strawberry.field(
        resolver=get_checked_in_students_resolver,
        description="Gets all students currently checked in to an event from Redis."
    )

    checkInCount: Optional[CheckInCount] = strawberry.field(
        resolver=get_check_in_count_resolver,
        description="Gets the current count of students checked in to an event from Redis."
    )


# --- Mutation Type ---

@strawberry.type
class Mutation:
    """Defines all the mutations (write operations) available in the Youth Group GraphQL API."""

    createEventType: EventType = strawberry.field(
        resolver=create_event_type_resolver,
        description="Creates a new event type with custom fields."
    )

    checkInStudent: bool = strawberry.field(
        resolver=check_in_student_resolver,
        description="Checks a student into an event. Returns true if successful."
    )

    checkOutStudent: bool = strawberry.field(
        resolver=check_out_student_resolver,
        description="Checks a student out of an event. Returns true if successful."
    )


# --- Schema ---

schema = strawberry.Schema(query=Query, mutation=Mutation)
