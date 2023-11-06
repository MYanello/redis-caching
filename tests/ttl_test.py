import redis
from src import app
import pytest
import argparse
import time
import cachetools


def test_ttl(): #ensure key values are getting removed after ttl is up
    args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 5, ttl = 1)
    app.launch_server('127.0.0.1', '9999')
    r = app.connect_backing(args)
    app.redis_data_gen(r, args.size)

    first_pull= app.get_data('3')
    second_pull = app.get_data('3') #second time to verify we pull value from cache
    time.sleep(1)
    third_pull = app.get_data('3') #third time to verify the value is no longer pulled from cache
    assert third_pull['source'] == 'redis'
    assert second_pull['source'] == 'cache'