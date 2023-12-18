import redis

# Connect to the Redis server
redis_host = 'localhost'
redis_port = 6379
redis_password = 'pass1232'
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# Add data to Redis
key = 'my_key'
value = 'Hello, Redis!'
redis_client.set(key, value)

print(f"Added data to Redis: Key={key}, Value={value}")
