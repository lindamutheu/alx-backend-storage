#!/usr/bin/env python3
"""
exercise.py
This module contains the Cache class with Redis storage and a replay function
for tracking method call history.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count how many times a method is called.
    Stores count in Redis under key: method.__qualname__
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store history of inputs and outputs for a method.
    Uses Redis lists: <method>:inputs and <method>:outputs
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        # Store input arguments as string (ignores kwargs)
        self._redis.rpush(input_key, str(args))

        # Call the original method and store output
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result
    return wrapper


class Cache:
    def __init__(self) -> None:
        """Initialize Redis client and flush the DB."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random UUID key.
        Returns the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self, key: str, fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float, None]:
        """
        Get data from Redis and optionally apply a conversion function.
        Returns None if key does not exist.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve data and decode bytes to UTF-8 string."""
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve data and convert bytes to int."""
        return self.get(key, fn=int)


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.
    Shows number of calls, inputs and outputs.
    """
    redis_client = method.__self__._redis
    method_name = method.__qualname__

    inputs_key = f"{method_name}:inputs"
    outputs_key = f"{method_name}:outputs"

    # Fetch all inputs and outputs
    inputs = redis_client.lrange(inputs_key, 0, -1)
    outputs = redis_client.lrange(outputs_key, 0, -1)

    # Number of calls = length of inputs (or outputs)
    call_count = len(inputs)

    print(f"{method_name} was called {call_count} times:")

    for input_bytes, output_bytes in zip(inputs, outputs):
        input_str = input_bytes.decode('utf-8')
        output_str = output_bytes.decode('utf-8')


print(
    f"{method_name}(*{input_str}) -> {output_str}"
)
