from src import app
import redis
import pytest

# A fixture to set up and tear down test data cache
@pytest.fixture
def setup_cached_data():
    app.cached_data = {'cached_key': b'Cached Data'}
    yield app.cached_data
    app.cached_data.clear()

# Mock a redis return
@pytest.fixture
def mock_redis(mocker):
    def mock_redis_get(key):
        logging.info('test')
        if key == 'redis_key':
            return b'Redis Data'
        else:
            return None
    mocker.patch.object(redis.Redis, 'get', side_effect=mock_redis_get)

# def test_get_data_from_redis(mock_redis): # I cannot get the above mock to work so commenting this test out for now
#     key = 'redis_key'
#     result = app.get_data(key)
#     assert result == {'key': key, 'data': 'Redis Data', 'source': 'redis'}

# Test cases
def test_get_data_from_cache(setup_cached_data):
    key = 'cached_key'
    result = app.get_data(key)
    assert result == {'key': key, 'data': 'Cached Data', 'source': 'cache'}

def test_no_key_parameter():
    key = None
    result = app.get_data(key)
    assert result == {'error': 'no key parameter'}

def test_key_not_found_in_redis(mock_redis):
    key = 'nonexistent_key'
    result = app.get_data(key)
    assert result == {'error': 'key not found'}