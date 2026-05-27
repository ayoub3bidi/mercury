import redis

from constants.settings import settings

redis_connect = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def init():
    global redis_client
    redis_client = redis_connect
