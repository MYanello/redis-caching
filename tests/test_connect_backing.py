import redis
from app import connect_backing
import pytest
import argparse

@pytest.mark.parametrize("host, port, pw, exception_type", [
    ("127.0.0.1", 6379, "rescale", None),
    ("1.1.1.1", 6379, "rescale", redis.exceptions.ConnectionError),
    ("127.0.0.1", 80, "rescale", redis.exceptions.ConnectionError),
    ("127.0.0.1", 6379, "", redis.exceptions.AuthenticationError),
])

def test_connect_backing(host, port, pw, exception_type):
    args = argparse.Namespace(redis_host = host, redis_port = port, pw = pw)
    assert connect_backing(args) == exception_type