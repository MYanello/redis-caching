import pytest
import argparse
import redis
import sys
import logging
from src import app

#sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.append("../src")

@pytest.fixture
def setup():
    args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 1, ttl = 1)
    application = app.redis_proxy(args)
    yield application
    application.clean()


