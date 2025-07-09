#!/usr/bin/env python3
"""
Expiring web cache and URL access tracker
"""
import redis
import requests
from functools import wraps
from typing import Callable


# Initialize Redis client
r = redis.Redis()


def count_url_access(func: Callable) -> Callable:
    """
    Decorator to increment the count of URL accesses.
    Stores count in Redis with key: count:{url}
    """
    @wraps(func)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        r.incr(count_key)
        return func(url)
    return wrapper


def cache_page(func: Callable) -> Callable:
    """
    Decorator to cache HTML content for 10 seconds.
    Stores cache in Redis with key: cache:{url}
    """
    @wraps(func)
    def wrapper(url: str) -> str:
        cache_key = f"cache:{url}"

        # Check if cached result exists
        cached = r.get(cache_key)
        if cached:
            return cached.decode('utf-8')

        # Call the original function and cache result
        html = func(url)
        r.setex(cache_key, 10, html)  # Cache for 10 seconds
        return html
    return wrapper


@count_url_access
@cache_page
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL.
    """
    response = requests.get(url)
    return response.text
