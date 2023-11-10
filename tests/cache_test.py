import redis
from src import app
import pytest
import argparse
import time
import cachetools
import logging

@pytest.fixture
def mock_redis(mocker):
    def mock_redis_get(key):
        if key == 'redis_key':
            return b'Redis Data'
        else:
            return None
    mocker.patch.object(app.redis.Redis, 'get', side_effect=mock_redis_get)


def test_ttl(mock_redis, standard_args): #ensure key values are getting removed after ttl is up
    app.connect_backing(standard_args)
    size = 5
    ttl = 1
    key = 'redis_key'
    app.cache_setup(size, ttl)
    #app.redis_data_gen(r, size)
    first_pull= app.get_data(key)
    logging.info(first_pull)
    second_pull = app.get_data(key) #second time to verify we pull value from cache
    logging.info(second_pull)
    time.sleep(ttl+1)
    third_pull = app.get_data(key) #third time to verify the value is no longer pulled from cache
    assert third_pull['source'] == 'redis'
    assert second_pull['source'] == 'cache'
    assert first_pull['source'] == 'redis'
#def test_size():