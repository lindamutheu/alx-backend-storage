#!/usr/bin/env python3
"""
Module cache
Defines a Cache class for storing data in Redis
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class that provides methods to store data in Redis
    """

    def __init__(self):
        """
        Initialize a Redis client and flush the database
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a random key

        Args:
            data (Union[str, bytes, int, float]): Data to store

        Returns:
            str: The key under which the data is stored
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

