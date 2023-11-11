from src import app
import pytest
import logging
import asyncio

def test_aio_get_data_from_redis(setup, mock_aioredis): 
    key = 'redis_key'
    application = setup
    result = asyncio.run(application.async_get_data(key))
    assert result == {'key': key, 'data': 'Redis Data', 'source': 'redis'}

# Test cases
def test_aio_get_data_from_cache(setup, mock_cached_data):
    application = setup
    application.cached_data = mock_cached_data
    key = 'cached_key'
    result = asyncio.run(application.async_get_data(key))
    assert result == {'key': key, 'data': 'Cached Data', 'source': 'cache'}

def test_aio_no_key_parameter(setup):
    key = None
    application = setup
    result = asyncio.run(application.async_get_data(key))
    assert result == {'error': 'no key parameter'}

def test_aio_key_not_found_in_redis(setup):
    application = setup
    key = 'nonexistent_key'
    result = asyncio.run(application.async_get_data(key))
    assert result == {'error': 'key not found'}