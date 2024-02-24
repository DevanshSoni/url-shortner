import redis
import os

redis_instance = redis.StrictRedis(
    host=os.environ.get('REDIS_HOST', '127.0.0.1'),
    port=os.environ.get('REDIS_PORT', '6379'),
    db=1
)
