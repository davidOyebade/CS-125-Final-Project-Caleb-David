"""
MongoDB Database Setup and Population Script for FP_YG_app
Westmont College CS 125 Database Design Fall 2025
Final Project - MongoDB Integration
Caleb Song & David Oyebade

This script:
1. Creates MongoDB collections for event types and custom event data
2. Populates collections with sample data matching the MySQL schema
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
load_dotenv("env")
mongo_client = None
# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Database name
MONGO_DB_NAME = "FP_YG_app"

def get_mongo_client():
    """Initializes and returns the MongoDB client."""
    global mongo_client
    if mongo_client is None:
        try:
            mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
            # Send a ping to confirm a successful connection
            mongo_client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            exit()
    return mongo_client
def get_mongo_db():
    """Gets the MongoDB database instance."""
    client = get_mongo_client()
    return client[MONGO_DB_NAME]
db = get_mongo_db()



# ========== STEP 1: DROP EXISTING COLLECTIONS (like TRUNCATE in SQL) ==========
print("\n--- Step 1: Dropping existing collections ---")
try:
    # Drop collections if they exist
    if "eventTypes" in db.list_collection_names():
        db["eventTypes"].drop()
        print("✓ Dropped 'eventTypes' collection")

    if "eventCustomData" in db.list_collection_names():
        db["eventCustomData"].drop()
        print("✓ Dropped 'eventCustomData' collection")

    print("Collections dropped successfully.")
except Exception as e:
    print(f"✗ Error dropping collections: {e}")

# ========== STEP 2: CREATE AND POPULATE eventTypes COLLECTION ==========
print("\n--- Step 2: Creating and populating 'eventTypes' collection ---")

# Collection for event type schemas (custom field definitions)
event_types_collection = db["eventTypes"]

# Event Type 1: Weekly Youth Night (ID 1)
event_type_1 = {
    "typeId": 1,
    "name": "Weekly Youth Night",
    "custom_fields": [
        {"field_name": "worship_theme", "data_type": "text"},
        {"field_name": "small_group_topic", "data_type": "text"},
        {"field_name": "snacks_provided", "data_type": "boolean"},
        {"field_name": "expected_attendance", "data_type": "number"}
    ]
}

# Event Type 2: Off-Site Retreat (ID 2)
event_type_2 = {
    "typeId": 2,
    "name": "Off-Site Retreat",
    "custom_fields": [
        {"field_name": "packing_list", "data_type": "text"},
        {"field_name": "bring_friend", "data_type": "boolean"},
        {"field_name": "accommodation_type", "data_type": "text"},
        {"field_name": "cost_per_person", "data_type": "number"},
        {"field_name": "meals_included", "data_type": "boolean"}
    ]
}

# Event Type 3: Service Project (ID 3)
event_type_3 = {
    "typeId": 3,
    "name": "Service Project",
    "custom_fields": [
        {"field_name": "project_location", "data_type": "text"},
        {"field_name": "tools_needed", "data_type": "text"},
        {"field_name": "dress_code", "data_type": "text"},
        {"field_name": "transportation_provided", "data_type": "boolean"},
        {"field_name": "lunch_provided", "data_type": "boolean"}
    ]
}

# Event Type 4: Program Training/Meeting (ID 4)
event_type_4 = {
    "typeId": 4,
    "name": "Program Training/Meeting",
    "custom_fields": [
        {"field_name": "agenda_items", "data_type": "text"},
        {"field_name": "materials_needed", "data_type": "text"},
        {"field_name": "required_attendance", "data_type": "boolean"},
        {"field_name": "certification_offered", "data_type": "boolean"}
    ]
}

# Event Type 5: Social/Party (ID 5)
event_type_5 = {
    "typeId": 5,
    "name": "Social/Party",
    "custom_fields": [
        {"field_name": "food_provided", "data_type": "boolean"},
        {"field_name": "dress_code", "data_type": "text"},
        {"field_name": "bring_friend", "data_type": "boolean"},
        {"field_name": "theme", "data_type": "text"},
        {"field_name": "activities", "data_type": "text"}
    ]
}

# Insert all event types
event_types = [event_type_1, event_type_2, event_type_3, event_type_4, event_type_5]
try:
    result = event_types_collection.insert_many(event_types)
    print(f"✓ Inserted {len(result.inserted_ids)} event type schemas")
    print(f"  - Event Type 1: Weekly Youth Night")
    print(f"  - Event Type 2: Off-Site Retreat")
    print(f"  - Event Type 3: Service Project")
    print(f"  - Event Type 4: Program Training/Meeting")
    print(f"  - Event Type 5: Social/Party")
except Exception as e:
    print(f"✗ Error inserting event types: {e}")

# ========== STEP 3: CREATE AND POPULATE eventCustomData COLLECTION ==========
print("\n--- Step 3: Creating and populating 'eventCustomData' collection ---")

# Collection for custom field values for specific event instances
event_custom_data_collection = db["eventCustomData"]

# Note: Event IDs from MySQL (from yg_data_insert.sql):
# Event 1: 'Weekly Youth Night - Jan' (Type 1)
# Event 2: 'Weekly Youth Night - Feb' (Type 1)
# Event 3: 'Spring Retreat' (Type 2)
# Event 4: 'Service Project' (Type 3)
# Event 5: 'Summer Kickoff' (Type 5)
# Event 6: 'Back-to-School Bash' (Type 5)
# Event 7: 'Christmas Party' (Type 5)
# Event 8: 'Volunteer Training' (Type 4)
# Event 9: 'Parent Info Night' (Type 4)
# Event 10: 'Outreach Booth' (Type 3)

# Event 1: Weekly Youth Night - Jan (Type 1)
event_custom_1 = {
    "eventId": 1,
    "typeId": 1,
    "custom_field_values": {
        "worship_theme": "New Beginnings",
        "small_group_topic": "Setting Goals for the Year",
        "snacks_provided": True,
        "expected_attendance": 45
    }
}

# Event 2: Weekly Youth Night - Feb (Type 1)
event_custom_2 = {
    "eventId": 2,
    "typeId": 1,
    "custom_field_values": {
        "worship_theme": "Love and Community",
        "small_group_topic": "Building Friendships",
        "snacks_provided": True,
        "expected_attendance": 50
    }
}

# Event 3: Spring Retreat (Type 2)
event_custom_3 = {
    "eventId": 3,
    "typeId": 2,
    "custom_field_values": {
        "packing_list": "Sleeping bag, pillow, toiletries, Bible, notebook, warm clothes, flashlight",
        "bring_friend": True,
        "accommodation_type": "Cabin with bunk beds",
        "cost_per_person": 75,
        "meals_included": True
    }
}

# Event 4: Service Project (Type 3)
event_custom_4 = {
    "eventId": 4,
    "typeId": 3,
    "custom_field_values": {
        "project_location": "Local Community Center",
        "tools_needed": "Paint brushes, rollers, drop cloths, cleaning supplies",
        "dress_code": "Work clothes that can get dirty",
        "transportation_provided": True,
        "lunch_provided": True
    }
}

# Event 5: Summer Kickoff (Type 5)
event_custom_5 = {
    "eventId": 5,
    "typeId": 5,
    "custom_field_values": {
        "food_provided": True,
        "dress_code": "Casual summer clothes",
        "bring_friend": True,
        "theme": "Beach Party",
        "activities": "Volleyball, water games, BBQ, bonfire"
    }
}

# Event 6: Back-to-School Bash (Type 5)
event_custom_6 = {
    "eventId": 6,
    "typeId": 5,
    "custom_field_values": {
        "food_provided": True,
        "dress_code": "School spirit wear",
        "bring_friend": True,
        "theme": "Back to School",
        "activities": "Games, music, food, school supply drive"
    }
}

# Event 7: Christmas Party (Type 5)
event_custom_7 = {
    "eventId": 7,
    "typeId": 5,
    "custom_field_values": {
        "food_provided": True,
        "dress_code": "Ugly Christmas sweaters encouraged",
        "bring_friend": True,
        "theme": "Christmas Celebration",
        "activities": "Gift exchange, caroling, hot chocolate, cookie decorating"
    }
}

# Event 8: Volunteer Training (Type 4)
event_custom_8 = {
    "eventId": 8,
    "typeId": 4,
    "custom_field_values": {
        "agenda_items": "Safety protocols, youth protection training, program overview, Q&A session",
        "materials_needed": "Notebook, pen, training manual",
        "required_attendance": True,
        "certification_offered": True
    }
}

# Event 9: Parent Info Night (Type 4)
event_custom_9 = {
    "eventId": 9,
    "typeId": 4,
    "custom_field_values": {
        "agenda_items": "Program introduction, calendar overview, volunteer opportunities, parent Q&A",
        "materials_needed": "Calendar, program brochure",
        "required_attendance": False,
        "certification_offered": False
    }
}

# Event 10: Outreach Booth (Type 3)
event_custom_10 = {
    "eventId": 10,
    "typeId": 3,
    "custom_field_values": {
        "project_location": "Community Fair at City Park",
        "tools_needed": "Table, chairs, flyers, sign-up sheets, pens",
        "dress_code": "Youth group t-shirts",
        "transportation_provided": False,
        "lunch_provided": False
    }
}

# Insert all custom event data
event_custom_data = [
    event_custom_1, event_custom_2, event_custom_3, event_custom_4, event_custom_5,
    event_custom_6, event_custom_7, event_custom_8, event_custom_9, event_custom_10
]

try:
    result = event_custom_data_collection.insert_many(event_custom_data)
    print(f"✓ Inserted {len(result.inserted_ids)} event custom data documents")
    print(f"  - Events 1-10 populated with custom field values")
except Exception as e:
    print(f"✗ Error inserting event custom data: {e}")

# ========== STEP 4: VERIFY DATA ==========
print("\n--- Step 4: Verifying data ---")
try:
    event_types_count = event_types_collection.count_documents({})
    event_custom_count = event_custom_data_collection.count_documents({})

    print(f"✓ Event Types collection: {event_types_count} documents")
    print(f"✓ Event Custom Data collection: {event_custom_count} documents")

    # Show a sample document from each collection
    print("\nSample Event Type (Type 1):")
    sample_type = event_types_collection.find_one({"typeId": 1})
    if sample_type:
        print(f"  Name: {sample_type['name']}")
        print(f"  Custom Fields: {len(sample_type['custom_fields'])}")
        for field in sample_type['custom_fields']:
            print(f"    - {field['field_name']} ({field['data_type']})")

    print("\nSample Event Custom Data (Event 3 - Spring Retreat):")
    sample_event = event_custom_data_collection.find_one({"eventId": 3})
    if sample_event:
        print(f"  Event ID: {sample_event['eventId']}")
        print(f"  Type ID: {sample_event['typeId']}")
        print(f"  Custom Values: {len(sample_event['custom_field_values'])} fields")
        for key, value in sample_event['custom_field_values'].items():
            print(f"    - {key}: {value}")

except Exception as e:
    print(f"✗ Error verifying data: {e}")

print("\n" + "=" * 60)
print("MongoDB database setup and population completed!")
print("=" * 60)
print("\nCollections created:")
print("  1. eventTypes - Event type schemas with custom field definitions")
print("  2. eventCustomData - Custom field values for event instances")
print("\nYou can now use these collections with api_implement.py")
print("=" * 60 + "\n")