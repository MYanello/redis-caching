from src import app
import pytest
import logging
import asyncio

def test_get_data_from_redis(setup, mock_redis):  #pull data from redis that isn't in the cache
    key = 'redis_key'
    application = setup
    result = asyncio.run(application.get_data(key))
    assert result == {'key': key, 'data': 'Redis Data', 'source': 'redis'}

# Test cases
def test_get_data_from_cache(setup, mock_cached_data): #pull data from cache if possible
    application = setup
    application.cached_data = mock_cached_data
    key = 'cached_key'
    result = asyncio.run(application.get_data(key))
    assert result == {'key': key, 'data': 'Cached Data', 'source': 'cache'}

def test_no_key_parameter(setup): #ensure we handle no key parameter correctly
    key = None
    application = setup
    result = asyncio.run(application.get_data(key))
    assert result == {'error': 'no key parameter'}

def test_key_not_found_in_redis(setup): #ensure we handle a key not found in redis correctly
    application = setup
    key = 'nonexistent_key'
    result = asyncio.run(application.get_data(key))
    assert result == {'error': 'key not found'}