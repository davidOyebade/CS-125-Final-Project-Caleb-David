"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-16262.c289.us-west-1-2.ec2.cloud.redislabs.com',
    port=16262,
    decode_responses=True,
    username="default",
    password="V9FaT0PWkXtJqJQPycmstGtZba6e7mGM",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

