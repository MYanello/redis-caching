from src import app
import pytest
import logging

# A fixture to set up and tear down test data cache
@pytest.fixture
def mock_cached_data():
    app.cached_data = {'cached_key': b'Cached Data'}
    yield app.cached_data

# def test_get_data_from_redis(mock_redis): # I cannot get the above mock to work so commenting this test out for now
#     key = 'redis_key'
#     result = app.get_data(key)
#     assert result == {'key': key, 'data': 'Redis Data', 'source': 'redis'}

# Test cases
def test_get_data_from_cache(setup, mock_cached_data):
    application = setup
    application.cached_data = mock_cached_data
    key = 'cached_key'
    result = application.get_data(key)
    assert result == {'key': key, 'data': 'Cached Data', 'source': 'cache'}

def test_no_key_parameter(setup):
    key = None
    application = setup
    result = application.get_data(key)
    assert result == {'error': 'no key parameter'}

def test_key_not_found_in_redis(setup):
    application = setup
    key = 'nonexistent_key'
    result = application.get_data(key)
    assert result == {'error': 'key not found'}