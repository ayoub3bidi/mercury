import redis

from constants.environment_variables import REDIS_HOST, REDIS_PORT

redis_connect = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def init():
    global redis_client
    redis_client = redis_connect