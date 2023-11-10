from fastapi import FastAPI
import uvicorn
import redis
from cachetools import TTLCache
import argparse
import logging
import time

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('--redis_port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('--proxy_host', type=str, help='The listening IP of the proxy', default='0.0.0.0')
parser.add_argument('--proxy_port', type=str, help='The listening port of the proxy', default='9999')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=10)
parser.add_argument('-k', '--size', type=int, help='Number of items to cache', default=10)
parser.add_argument('--password', type=str, nargs='?')

class redis_proxy:
    def __init__(self, args):
        self.args = args
        self.cached_data = self.cache_setup()
        self.app = FastAPI()
        @self.app.get('/get_data')
        def get_data(key): #pull data from redis or cache if possible
            if not key:
                return ({'error': 'no key parameter'})
            if key in self.cached_data:
                return ({'key': key, 'data': self.cached_data[key].decode('utf-8'), 'source': 'cache'})
            try:
                logging.info('redis get')
                redis_value = self.r.get(key)
                logging.info(self.r)
                self.cached_data[key] = redis_value
                return ({'key': key, 'data':redis_value.decode('utf-8'), 'source': 'redis'})
            except Exception as e:
                logging.error(f"Error getting data from Redis: {e}")
                return ({'error': 'key not found'})
        @self.app.middleware("http") # track the speed of our calls
        async def add_process_time_header(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
            return(response)
        
    def redis_data_gen(self, size):
        for i in range(size):
            self.r.set(i, i**2)
        logging.info("Added test data to Redis instance")
    def connect_backing(self): # connect to the redis instance
        try:
            self.r = redis.Redis(host=self.args.redis_host, port=self.args.redis_port, db=0, password=self.args.password, socket_timeout=1)
            self.r.ping()
        except redis.exceptions.AuthenticationError as e: 
            logging.critical(f"Redis password required: {e}")
        except redis.exceptions.ConnectionError or redis.exceptions.TimeoutError as e:
            logging.critical(f"Redis connection error: {e}")
        logging.info('Connect backing')
        return(self.r)
    def cache_setup(self):
        self.cached_data = TTLCache(maxsize = self.args.size, ttl = self.args.ttl)
        logging.info(f"Created cache with TTL {self.args.ttl} and size {self.args.size}")
        return(self.cached_data)
    def launch_server(self):
        uvicorn.run(self.app, host=self.args.proxy_host, port=self.args.proxy_port)
    def clean(self):
        self.r.flushall()
    def print_properties(self):
        for attr_name, attr_value in vars(self).items():
            logging.info(f"{attr_name}: {attr_value}")

if __name__ == '__main__':
    args = parser.parse_args()
    app = redis_proxy(args)
    app.connect_backing()
    app.clean()
    app.redis_data_gen(3)
    app.print_properties()
    app.launch_server()
