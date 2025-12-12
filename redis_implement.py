#Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
# Caleb Song & David Oyebade

import redis
import os
from dotenv import load_dotenv

load_dotenv("env")


redis_client = None
def get_redis_client():
    """Initializes and returns the Redis client."""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host= os.getenv("redis_host"),
                port=16262,
                decode_responses=True,
                username="default",
                password=os.getenv("redis_password"),
            )
            # Check connection
            redis_client.ping()
            print("Successfully connected to Redis!")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            exit()
    return redis_client
def get_redis_conn():
    """Gets the Redis client instance."""
    return get_redis_client()
def close_connections():
    """Close all database connections."""
    # MySQL pool doesn't have an explicit close, connections are returned to pool.
    # Redis client doesn't require explicit closing for this library version
    # when used like this, but it's good practice if a close method is available.
    print("Connection cleanup finished.")

