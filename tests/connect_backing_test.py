import redis
from src import app
import pytest
import argparse

@pytest.mark.parametrize("host, port, pw, exception_type", [
    ("127.0.0.1", "6379", "rescale", None),
    ("1.1.1.1", "6379", "rescale", redis.exceptions.ConnectionError),
    ("127.0.0.1", "80", "rescale", redis.exceptions.ConnectionError),
    ("127.0.0.1", "6379", "bad_pw", redis.exceptions.AuthenticationError),
    ("127.0.0.1", "6379", "", redis.exceptions.AuthenticationError)
])

def test_connect_backing(host, port, pw, exception_type):
    args = argparse.Namespace(redis_host = host, redis_port = port, password = pw)
    assert app.connect_backing(args) == exception_type
    # try:
    #     connect_backing(args)
    # except Exception as e:
    #     print(e)
    #     assert isinstance(e, exception_type)