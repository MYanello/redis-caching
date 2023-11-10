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
    application.redis_data_gen(1000)
    proc = Process(target=application.launch_server, args=(), daemon=True)
    proc.start()
    time.sleep(1)
    yield 
    proc.kill()
    application.clean()

def test_api(server):
    response = requests.get('http://localhost:9999/get_data?key=1')
    assert response.json()['data'] == "1"