#Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
# Caleb Song & David Oyebade
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri =  ""
mongo_client = None

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

MONGO_URI = uri
MONGO_DB_NAME = "bakery_reviews"

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

def close_connections():
    """Close all database connections."""
    # MySQL pool doesn't have an explicit close, connections are returned to pool.
    # MongoDB client should be closed if the app is shutting down.
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")
    # Redis client doesn't require explicit closing for this library version
    # when used like this, but it's good practice if a close method is available.
    print("Connection cleanup finished.")


def setup_mongo_data():
    """
    Connects to MongoDB, clears the 'product_reviews' collection,
    and populates it with semantically meaningful, fake bakery review data.
    """
    try:
        db = get_mongo_db()
        reviews_collection = db["product_reviews"]

        # Clear existing data to ensure a clean slate for the demo
        print("Clearing existing data from 'product_reviews' collection...")
        reviews_collection.delete_many({})
        print("Collection cleared.")

        # Sample review data linked to product IDs from the MySQL database
        reviews_data = [
            {
                "product_id": "20-BC-C-10",  # Chocolate Cake
                "reviews": [
                    {
                        "customer_id": 1,
                        "rating": 5,
                        "comment": "Absolutely decadent! The best chocolate cake I've ever had.",
                        "tags": ["rich", "chocolatey", "dessert"],
                        "timestamp": datetime(2023, 10, 26, 14, 30)
                    },
                    {
                        "customer_id": 8,
                        "rating": 4,
                        "comment": "Very good, but a little too sweet for me.",
                        "tags": ["sweet", "rich"],
                        "timestamp": datetime(2023, 10, 25, 18, 0)
                    }
                ]
            },
            {
                "product_id": "90-APIE-10",  # Apple Pie
                "reviews": [
                    {
                        "customer_id": 5,
                        "rating": 5,
                        "comment": "A classic apple pie, just like my grandma used to make. The crust was perfect.",
                        "image_url": "https://example.com/fake-images/apple-pie.jpg",
                        "tags": ["classic", "homestyle", "fruit"],
                        "timestamp": datetime(2023, 10, 27, 11, 0)
                    },
                    {
                        "customer_id": 6,
                        "rating": 5,
                        "comment": "Superb! You can taste the fresh apples.",
                        "tags": ["fresh", "perfect crust"],
                        "timestamp": datetime(2023, 10, 28, 19, 45)
                    }
                ]
            },
            {
                "product_id": "50-CH",  # Chocolate Croissant
                "reviews": [
                    {
                        "customer_id": 18,
                        "rating": 5,
                        "comment": "Flaky, buttery, and filled with delicious chocolate. A perfect breakfast treat.",
                        "tags": ["buttery", "flaky", "breakfast"],
                        "timestamp": datetime(2023, 11, 1, 9, 5)
                    }
                ]
            }
        ]

        # Insert the new data
        print("Inserting new sample review data...")
        reviews_collection.insert_many(reviews_data)
        print(f"{len(reviews_data)} product review documents inserted successfully.")

    except Exception as e:
        print(f"An error occurred during MongoDB setup: {e}")
    finally:
        # Close the connection
        close_connections()

if __name__ == "__main__":
    print("--- Starting MongoDB Data Setup ---")
    setup_mongo_data()
    print("--- MongoDB Data Setup Finished ---")
