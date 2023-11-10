from src import app
import pytest
import argparse
import logging
import requests
import uvicorn

@pytest.fixture
def server():
    server = uvicorn.run(app, host='0.0.0.0', port='9999')
    with server.run_in_thread():
        yield server

def test_api():
    args = argparse.Namespace(proxy_host = '0.0.0.0', proxy_port = '9999', redis_host = '127.0.0.1', redis_port = '6379', password = 'rescale', size = 100, ttl = 100)
    application = app.redis_proxy(args)
    application.redis_data_gen(1000)
    application.launch_server()
    #assert True
    response = requests.get('http://localhost:9999/get_data?key=1')
    assert response['data'] == 1
    application.clean()



'''To join the video meeting, click this link: https://meet.google.com/ozz-mpan-kjm
Otherwise, to join by phone, dial +1 585-491-9371 and enter this PIN: 169 613 442#
To view more phone numbers, click this link: https://tel.meet/ozz-mpan-kjm?hs=5'''
