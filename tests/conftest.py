import sys
import os
from src import app
import pytest
import argparse

#sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# @pytest.fixture
# def redis_client(test_args):
#     r = app.connect_backing(test_vargs)
#     return(r)


# @pytest.fixture
# def data_gen():
#     app.redis_data_gen(r, 10)

# @pytest.fixture
# def test_args(size, ttl):
#     args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = size, ttl = ttl)
#     r = redis_client(args)
#     return(args, r)

# @pytest.fixture(scope="session")
# def proxy_start():
#     server = app.launch_server('127.0.0.1', '9999')

@pytest.fixture
def setup_teardown():
    args = argparse.Namespace(redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 10, ttl = 1)
    r = app.connect_backing(args)
    app.redis_data_gen(r, 100)
    yield
    print('teardown')