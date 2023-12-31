import redis
from src import app
import pytest
import argparse

@pytest.mark.parametrize("host, port, pw, exception_type", [ # maybe test using caplog instead of exceptions, but this works for ensuring we connect to backends correctly
    ("127.0.0.1", "6379", "rescale", None),
    ("203.0.113.1", "6379", "rescale", redis.exceptions.TimeoutError),
    ("127.0.0.1", "80", "rescale", redis.exceptions.ConnectionError),
    ("127.0.0.1", "6379", "bad_pw", redis.exceptions.AuthenticationError),
    ("127.0.0.1", "6379", "", redis.exceptions.AuthenticationError)
])

def test_connect_backing(host, port, pw, exception_type):
    args = argparse.Namespace(redis_host = host, redis_port = port, password = pw, size = 10, ttl = 10)
    if exception_type is None:
        try:
            application = app.redis_proxy(args)
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")
    else:
        with pytest.raises(exception_type):
            application = app.redis_proxy(args)

