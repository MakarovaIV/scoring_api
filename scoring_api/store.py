import logging
import time

import redis


class Store(object):

    def __init__(self, connect_params, custom_config):
        self.connect_params = connect_params
        self.redis_client = None
        self.redis_client = redis.Redis(**self.connect_params)
        self.reconnect_attempts = custom_config["reconnect_attempts"] if "reconnect_attempts" in custom_config else 3

    def get(self, key):
        attempts = self.reconnect_attempts
        while attempts:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                attempts -= 1
                logging.error("Cannot get value from Redis")
                time.sleep(2)

    def get_list(self, key):
        attempts = self.reconnect_attempts
        while attempts:
            try:
                return self.redis_client.lrange(key, 0, -1)
            except Exception as e:
                attempts -= 1
                logging.error("Cannot get list of values from Redis")
                time.sleep(2)

    def set(self, key, value):
        attempts = self.reconnect_attempts
        while attempts:
            try:
                return self.redis_client.set(key, value)
            except Exception as e:
                attempts -= 1
                logging.error("Cannot set value to Redis")
                time.sleep(2)

    def set_list(self, key, value):
        attempts = self.reconnect_attempts
        while attempts:
            try:
                self.redis_client.delete(key)
                return self.redis_client.rpush(key, *value)
            except Exception as e:
                attempts -= 1
                logging.error("Cannot set value to Redis")
                time.sleep(2)

    def cache_get(self, key):
        return self.redis_client.get(key)

    def cache_set(self, key, value, expire_timeout):
        self.redis_client.set(key, value)
        self.redis_client.expire(key, expire_timeout)
