from multiprocessing import Process
import aiohttp
import logging
from src import app
import pytest
import argparse
import requests
import time
import json

@pytest.fixture
def server():
    args = argparse.Namespace(proxy_host = '0.0.0.0', proxy_port = '9999', redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 100, ttl = 100)
    application = app.redis_proxy(args)
    application.redis_data_gen(1000)
    proc = Process(target=application.launch_server, args=(), daemon=True)
    proc.start()
    time.sleep(1) #give a second to bring up the server before yielding
    yield 
    proc.kill()
    application.clean()

def test_api(server): #don't pytest.mark.parametrize because we want to start the server only once to test the cacheing
    assert_get_data(5, "25", "redis")
    assert_get_data(5, "25", "cache")

def assert_get_data(key, expected_data, expected_source): #ensure the api is caching keys correctly
    response = requests.get(f'http://localhost:9999/get_data?key={key}')
    assert response.json()['data'] == expected_data
    assert response.json()['source'] == expected_source

@pytest.mark.asyncio #ensure we handle async requests correctly
async def test_async_reqs(server):
    runs = 1000
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        for i in range(runs):
            url = f'http://localhost:9999/get_data?key={i}'
            response = await session.get(url)
            response = await response.json()
            logging.debug(response)
            expected_data = str(int(i)**2)
            assert response['data'] == expected_data
    run_time = time.time() - start_time
    logging.info(f"Time to run {runs} requests: {run_time:0.4f} seconds")

        
def test_seq_reqs(server):
    runs = 1000
    start_time = time.time()
    for i in range(runs):
        expected_data = str(int(i)**2)
        response = requests.get(f'http://localhost:9999/get_data?key={i}')
        assert response.json()['data'] == expected_data
    run_time = time.time() - start_time
    logging.info(f"Time to run {runs} requests: {run_time:0.4f} seconds")