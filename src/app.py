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
        self.r = self.connect_backing()
        self.app = FastAPI()
        @self.app.get('/get_data')(self.get_data)

        @self.app.middleware("http") 
        async def add_process_time_header(request, call_next):
            #track api call speed
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
            return(response)
        
    def get_data(self, key) -> dict: 
        #pull data from redis or cache if possible
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

    async def async_get_data(self, key) -> dict: 
        #pull data from redis or cache if possible asynchronously
        if not key:
            return ({'error': 'no key parameter'})
        if key in self.cached_data:
            return ({'key': key, 'data': self.cached_data[key].decode('utf-8'), 'source': 'cache'})
        try:
            logging.info('redis get')
            redis_value = await self.r.get(key)
            if redis_value is not None:
                redis_value = redis_value.decode('utf-8')
                self.cached_data[key] = redis_value
                return ({'key': key, 'data':redis_value.decode('utf-8'), 'source': 'redis'})
        except Exception as e:
            logging.error(f"Error getting data from Redis: {e}")
            return ({'error': 'key not found'})

    def redis_data_gen(self, size):
        #generate test data in redis
        for i in range(size):
            self.r.set(i, i**2)
        logging.info("Added test data to Redis instance")

    def connect_backing(self) -> redis.Redis: 
        #connect to the backing redis instance
        try:
            self.r = redis.Redis(host=self.args.redis_host, port=self.args.redis_port, db=0, password=self.args.password, socket_timeout=1)
            self.r.ping()
        except redis.exceptions.AuthenticationError as e: 
            logging.critical(f"Redis password error: {e}")
            raise
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logging.critical(f"Redis connection error: {e}")
            raise
        logging.debug('Connect backing')
        return(self.r)
    
    def cache_setup(self):
        #create a cache with the specified TTL and size
        self.cached_data = TTLCache(maxsize = self.args.size, ttl = self.args.ttl)
        logging.debug(f"Created cache with TTL {self.args.ttl} and size {self.args.size}")
        return(self.cached_data)
    
    def launch_server(self):
        uvicorn.run(self.app, host=self.args.proxy_host, port=self.args.proxy_port)
        # config = uvicorn.config(self.app, host=self.args.proxy_host, port=self.args.proxy_port)
        # server = uvicorn.Server(config=config)
        # await server.serve()

    def clean(self):
        #empty redis and cache, use with caution
        self.r.flushall()
        self.cached_data.clear()

    def print_properties(self):
        #print all properties of the class for testing
        return {attr_name: attr_value for attr_name, attr_value in vars(self.items())}

if __name__ == '__main__':
    args = parser.parse_args()
    app = redis_proxy(args)
    app.redis_data_gen(100)
    app.launch_server()
