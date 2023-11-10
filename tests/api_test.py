from multiprocessing import Process
from src import app
import pytest
import argparse
import logging
import requests
import uvicorn
import time
import json

@pytest.fixture
def server():
    args = argparse.Namespace(proxy_host = '0.0.0.0', proxy_port = '9999', redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 100, ttl = 100)
    application = app.redis_proxy(args)
    application.redis_data_gen(10)
    proc = Process(target=application.launch_server, args=(), daemon=True)
    proc.start()
    time.sleep(1) #give a second to bring up the server before yielding
    yield 
    proc.kill()
    application.clean()

def test_api(server):
    assert_get_data(5, "25", "redis")
    assert_get_data(5, "25", "cache")

def assert_get_data(key, expected_data, expected_source):
    response = requests.get(f'http://localhost:9999/get_data?key={key}')
    assert response.json()['data'] == expected_data
    assert response.json()['source'] == expected_source