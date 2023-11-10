from fastapi import FastAPI
import uvicorn
import redis
from cachetools import TTLCache
import argparse
import logging

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('--redis_port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('--proxy_host', type=str, help='The listening IP of the proxy', default='0.0.0.0')
parser.add_argument('--proxy_port', type=str, help='The listening port of the proxy', default='9999')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=10)
parser.add_argument('-k', '--size', type=int, help='Number of items to cache', default=10)
parser.add_argument('--password', type=str, nargs='?')
parser.add_argument('-T', '--test', action='store_true', help='Run tests')
args = parser.parse_args()
cached_data = TTLCache(maxsize = args.size, ttl = args.ttl)

def cache_setup(size, ttl):
    cached_data = TTLCache(maxsize = size, ttl = ttl)
    logging.info(f"Created cache with TTL {ttl} and size {size}")
    return(cached_data)

def redis_data_gen(r, size):
    for i in range(size):
        r.set(i, i**2)
    logging.info("Added test data to Redis instance")

# def test_lru(r, args):
#     #orig_size = args.size
#     #args.size = 2
#     #cache_param(600, args.size)
#     redis_data_gen(r, args.size)
#     logging.info(r.get('1'))
#     #cache_param(orig_size, args.ttl)

def clean(r, cached_data):
    cached_data.cache_clear()

app = FastAPI()
def connect_backing(args): # connect to the redis instance
    try:
        r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0, password=args.password, socket_timeout=1)
        r.ping()
    except redis.exceptions.AuthenticationError as e: 
        logging.critical(f"Redis password required: {e}")
        raise
    except redis.exceptions.ConnectionError or redis.exceptions.TimeoutError as e:
        logging.critical(f"Redis connection error: {e}")
        raise
    logging.info('Connect backing')
    return(r)
@app.get('/get_data')
def get_data(key): #pull data from redis or cache if possible
    if not key:
        return ({'error': 'no key parameter'})
    if key in cached_data:
        return ({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'cache'})
    try:
        logging.info('redis get')
        redis_value = r.get(key)
        logging.info(r)
        cached_data[key] = redis_value
        return ({'key': key, 'data':redis_value.decode('utf-8'), 'source': 'redis'})
    except:
        return ({'error': 'key not found'})


# @app.put('/cache_params') #this wipes the current cache, provide cache update function instead if time permits
# def cache_param(size: int = None, ttl: int = None):
#     if size:
#         if ttl:
#             args.size, args.ttl = size, ttl
#         else:
#             args.size = size
#     if ttl and not size:
#         args.ttl = ttl
#     cache_setup(args)


@app.middleware("http") # track the speed of our calls
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
    return response

def launch_server(host, port):
    uvicorn.run(app, host=host, port=port)
        
if __name__ == '__main__':
    r = connect_backing(args)
    cached_data = cache_setup(args.size, args.ttl)
    #cached_data = cache_setup(args.size, args.ttl)
    launch_server(args.proxy_host, args.proxy_port)