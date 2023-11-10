import redis
from src import app
import pytest
import argparse
import time
import cachetools
import logging

def test_ttl(setup, mock_redis): #ensure key values are getting removed after ttl is up
    application = setup
    key = 'redis_key'
    first_pull= application.get_data(key)
    logging.info(first_pull)
    second_pull = application.get_data(key) #second time to verify we pull value from cache
    logging.info(second_pull)
    time.sleep(1)
    third_pull = application.get_data(key) #third time to verify the value is no longer pulled from cache
    assert third_pull['source'] == 'redis'
    assert second_pull['source'] == 'cache'
    assert first_pull['source'] == 'redis'

def test_size():
    args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 1, ttl = 100)
    application = app.redis_proxy(args)
    application.redis_data_gen(10)
    assert application.get_data(1)['source'] == 'redis'
    assert application.get_data(1)['source'] == 'cache' # make sure first pull is cached
    assert application.get_data(2)['source'] == 'redis' # make sure second pull is not cached
    assert application.get_data(1)['source'] == 'redis' # make sure first pull is removed from the cache by second pull
