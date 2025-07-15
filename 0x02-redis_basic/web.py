#!/usr/bin/env python3
"""
This module implements a get_page function that fetches HTML content
of a URL, caches it for 10 seconds, and tracks how many times
each URL is accessed in Redis.

Author: Linda Musyoki
"""
import redis
import requests
from functools import wraps
from typing import Callable


# Initialize Redis client
r = redis.Redis()


def cache_page(func: Callable) -> Callable:
    """
    Decorator to cache HTML content for 10 seconds.
    Stores cache in Redis with key: cache:{url}
    """
    @wraps(func)
    def wrapper(url: str) -> str:
        cache_key = f"cache:{url}"
        count_key = f"count:{url}"

        # Check if cached result exists
        cached = r.get(cache_key)
        if cached:
            return cached.decode('utf-8')

        # Cache miss: fetch, increment count, cache result
        html = func(url)
        r.incr(count_key)  # Increment count only on fetch
        r.setex(cache_key, 10, html)  # Cache for 10 seconds
        return html
    return wrapper


@cache_page
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL.
    """
    response = requests.get(url)
    return response.text
