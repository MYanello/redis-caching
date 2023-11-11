from fastapi import FastAPI
import uvicorn
import redis
from cachetools import TTLCache
import argparse
import logging
import time
import aioredis


logging.basicConfig(level=logging.DEBUG)
parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('--redis_port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('--proxy_host', type=str, help='The listening IP of the proxy', default='0.0.0.0')
parser.add_argument('--proxy_port', type=str, help='The listening port of the proxy', default='9999')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=10)
parser.add_argument('-k', '--size', type=int, help='Number of items to cache', default=10)
parser.add_argument('--password', type=str, nargs='?')

class RedisProxy:
    def __init__(self, args):
        self.args = args
        self.cached_data = self.cache_setup()
        self.r = self.connect_backing()
        self.pool = self.aioredis_pool()
        self.app = FastAPI()
        @self.app.get('/get_data')(self.get_data)
        @self.app.get('/get_data_async')(self.async_get_data)
        @self.app.middleware("http") 
        async def add_process_time_header(request, call_next):
            #track api call speed
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
            return response
        
    def get_data(self, key) -> dict: 
        #pull data from redis or cache if possible
        if not key:
            return ({'error': 'no key parameter'})
        if key in self.cached_data:
            return ({'key': key, 'data': self.cached_data[key].decode('utf-8'), 'source': 'cache'})
        try:
            redis_value = self.r.get(key)
            logging.debug(self.r)
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
            async with self.pool.get_connection() as conn: #get a connection from the pool to run the command with
                redis_value = await self.pool.execute(b'GET', key)
                if redis_value is not None:
                    redis_value = redis_value.decode('utf-8')
                    self.cached_data[key] = redis_value
                    return ({'key': key, 'data':redis_value, 'source': 'redis'})
        except Exception as e:
            logging.error(f"Error getting data: {e}")
            return ({'error': 'key not found'})

    async def aioredis_pool(self):
        #connect to the backing redis instance asynchronously
        logging.debug('Creating pool from backing instance with AIORedis')
        try:
            if self.args.password:
                self.pool = await aioredis.create_pool((self.args.redis_host, self.args.redis_port), password = self.args.password, create_connection_timeout=1)
            else:
                self.pool = await aioredis.create_pool((self.args.redis_host, self.args.redis_port), create_connection_timeout=1)
            logging.debug('Created pool from backing instance with AIORedis')
        except aioredis.exceptions.AuthenticationError as e: 
            logging.critical(f"Redis password error: {e}")
        except (aioredis.exceptions.ConnectionError, aioredis.exceptions.TimeoutError) as e:
            logging.critical(f"Redis connection error: {e}")
        logging.debug(self.pool)
        return self.pool
    
    
    def connect_backing(self) -> redis.Redis: 
        #connect to the backing redis instance
        try:
            if self.args.password:
                self.r = redis.Redis(host=self.args.redis_host, port=self.args.redis_port, db=0, password=self.args.password, socket_timeout=1)
            else:
                self.r = redis.Redis(host=self.args.redis_host, port=self.args.redis_port, db=0, socket_timeout=1)
            self.r.ping()
            logging.info('Connected to backing instance with Redis')
        except redis.exceptions.AuthenticationError as e: 
            logging.critical(f"Redis password error: {e}")
            raise
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            logging.critical(f"Redis connection error: {e}")
            raise
        return self.r


    def cache_setup(self):
        #create a cache with the specified TTL and size
        self.cached_data = TTLCache(maxsize = self.args.size, ttl = self.args.ttl)
        logging.debug(f"Created cache with TTL {self.args.ttl} and size {self.args.size}")
        return(self.cached_data)
    
    def launch_server(self):
        #launch redis proxy server
        uvicorn.run(self.app, host=self.args.proxy_host, port=int(self.args.proxy_port))

    def clean(self):
        #empty redis and cache, use with caution
        self.r.flushall()
        self.cached_data.clear()

    def redis_data_gen(self, size):
        #generate test data in redis
        for i in range(size):
            self.r.set(i, i**2)
        logging.debug("Added test data to Redis instance")

    def print_properties(self):
        #print all properties of the class for testing
        return {attr_name: attr_value for attr_name, attr_value in vars(self.items())}

if __name__ == '__main__':
    args = parser.parse_args()
    app = RedisProxy(args)
    app.redis_data_gen(100)
    app.launch_server()
