import pytest
import argparse
from src import app

@pytest.fixture
def setup(): #setup the application with a small cache size and ttl
    args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 1, ttl = 1)
    application = app.redis_proxy(args)
    yield application
    application.clean()

@pytest.fixture # A fixture to set up and tear down test data cache
def mock_cached_data():
    app.cached_data = {'cached_key': b'Cached Data'}
    yield app.cached_data
    app.cached_data.clear()

@pytest.fixture # A fixture to mock the redis get method so we can test without a redis server
def mock_redis(mocker):
    def mock_redis_get(key):
        if key == 'redis_key':
            return b'Redis Data'
        else:
            return None
    mocker.patch('redis.Redis.get', side_effect=mock_redis_get)
