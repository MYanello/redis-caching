from src import app
import pytest
import argparse
import time
import logging
import asyncio

def test_ttl(setup, mock_redis): #ensure key values are getting removed after ttl is up
    application = setup
    key = 'redis_key'
    first_pull= asyncio.run(application.get_data(key))
    logging.debug(first_pull)
    second_pull = asyncio.run(application.get_data(key)) #second time to verify we pull value from cache
    logging.debug(second_pull)
    time.sleep(1)
    third_pull = asyncio.run(application.get_data(key)) #third time to verify the value is no longer pulled from cache
    assert third_pull['source'] == 'redis'
    assert second_pull['source'] == 'cache'
    assert first_pull['source'] == 'redis'

def test_size(): #make sure that the cache is clearing when filled
    args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 1, ttl = 100)
    application = app.redis_proxy(args)
    application.redis_data_gen(10)
    assert asyncio.run(application.get_data(1))['source'] == 'redis'
    assert asyncio.run(application.get_data(1))['source'] == 'cache' # make sure first pull is cached
    assert asyncio.run(application.get_data(2))['source'] == 'redis' # make sure second pull is not cached
    assert asyncio.run(application.get_data(1))['source'] == 'redis' # make sure first pull is removed from the cache by second pull
