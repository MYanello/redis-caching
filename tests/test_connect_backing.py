import redis
import app
import pytest

@pytest.mark.parametrize("host, port, pw, exception_type", [
    ("127.0.0.1", 6379, "rescale", None),
    ("1.1.1.1", 6379, "rescale", redis.exceptions.ConnectionError)
    ("127.0.0.1", 80, "rescale", redis.exceptions.ConnectionError),
    ("127.0.0.1", 6379, "", redis.exceptions.AuthenticationError),
])

def test_connect_backing():
    assert connect_backing(r) == 'Backing Redis connection successful'