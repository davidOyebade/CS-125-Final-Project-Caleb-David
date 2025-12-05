import redis
import os
from dotenv import load_dotenv

load_dotenv()


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

def setup_redis_data():
    """
    Connects to Redis and sets up the 'daily_deal' hash with
    a product ID and a discount percentage.
    """
    try:
        r = get_redis_conn()

        # Define the daily deal data
        daily_deal_key = "daily_deal"
        deal_product_id = "50-CH"  # Chocolate Croissant
        deal_discount = 20  # 20% off

        # Use HSET to store the deal as a hash
        print(f"Setting up the daily deal in Redis for product: {deal_product_id}...")
        r.hset(daily_deal_key, mapping={
            "product_id": deal_product_id,
            "discount_percent": deal_discount
        })

        print("Daily deal setup successfully.")

        # Verify the data was set
        retrieved_deal = r.hgetall(daily_deal_key)
        print(f"Verified data from Redis: {retrieved_deal}")

    except Exception as e:
        print(f"An error occurred during Redis setup: {e}")
    finally:
        # No explicit close needed for this library version in this context
        close_connections()

if __name__ == "__main__":
    print("--- Starting Redis Data Setup ---")
    setup_redis_data()
    print("--- Redis Data Setup Finished ---")
