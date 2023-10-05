import os
import redis

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_connect = redis.Redis(host=redis_host, port=redis_port)

def init():
    global redis_client
    redis_client = redis_connect