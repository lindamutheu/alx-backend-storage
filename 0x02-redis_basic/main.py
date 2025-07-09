#!/usr/bin/env python3
"""
Test the Cache class
"""

from cache import Cache

cache = Cache()

# Test storing different data types
key1 = cache.store("Hello Redis!")
key2 = cache.store(123)
key3 = cache.store(45.67)
key4 = cache.store(b"bytes data")

print("Stored keys:")
print(key1)
print(key2)
print(key3)
print(key4)
