from fastapi import FastAPI
import uvicorn
import time
import sys
import redis
from cachetools import TTLCache
import argparse

parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('--redis_port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('--proxy_host', type=str, help='The listening IP of the proxy', default='0.0.0.0')
parser.add_argument('--proxy_port', type=int, help='The listening port of the proxy', default='9209')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=10)
parser.add_argument('-k', '--size', type=int, help='Number of items to cache', default=10)
parser.add_argument('--pw', type=str, nargs='?')
parser.add_argument('-T', '--test', action='store_true', help='Run tests')
args = parser.parse_args()


def connect_backing(args): # connect to the redis instance
    try:
        r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0, password=args.pw)
    except redis.exceptions.AuthenticationError as e: 
        print(f"Redis password required: {e}")
        sys.exit(1)
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}")
        sys.exit(1)
    redis_test_conn(r)
    return(r)

def cache_setup(args):
    cached_data = TTLCache(maxsize = args.size, ttl = args.ttl)
    #print(f"TTL = {args.ttl} and Size = {args.size}")
    #print('Created TTL LRU cache')
    return(cached_data)

def redis_test_conn(r): 
    try:
        response = r.ping()
        if response:
            print("Backing Redis connection successful")
        else:
            print("Unable to connect to Redis instance")
            sys.exit(1)
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis instance: {e}")
        sys.exit(1)

def redis_data_gen(r, size): # create some test data that just squares the key and fills the cache
    for i in range(size-1):
        r.set(i, i**2)
    print("Added test data to Redis instance")

def test_ttl(r, args): #ensure key values are getting removed after ttl is up
    ttl_param(1)
    orig_ttl = args.ttl
    redis_data_gen(r, args.size)
    first_caching = get_data('1') #first time to cache the value
    second_caching = get_data('1') #second time to verify we pull value from cache
    print(second_caching)
    time.sleep(args.ttl+1)
    third_caching = get_data('1') #third time to verify the value is no longer pulled from cache
    print(third_caching)
    if third_caching['source'] == 'redis' and second_caching['source'] == 'cache':
        print(f"Cached value removed after {args.ttl} seconds.")
    else:
        print(f"Cached value not removed after TTL")
    ttl_param(orig_ttl)

def test_lru(r, args):
    orig_size = args.size
    test_size = 3
    size_param(test_size)
    redis_data_gen(r, test_size-1)
    for i in range(test_size):
        
        print(cached_data[i])
    size_param(orig_size)
    return

def clean(r, cached_data):
    cached_data.cache_clear()
    return

app = FastAPI()
@app.get('/get_data')
def get_data(key: int): #pull data from redis or cache if possible
    if not key:
        return ({'error': 'no key parameter'})
    if key in cached_data:
        return ({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'cache'})
    try:
        redis_value = r.get(key)
        cached_data[key] = redis_value
        return ({'key': key, 'data':redis_value.decode('utf-8'), 'source': 'redis'})
    except:
        return ({'error': 'key not found in redis'})
@app.put('/cache_params/size')
def size_param(size: int):
    args.size = size
    cache_setup(args)
    return
@app.put('/cache_params/ttl')
def ttl_param(ttl: int): 
    args.ttl = ttl
    cache_setup(args)
    return
    

@app.middleware("http") # track the speed of our calls
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
    return response

if __name__ == '__main__':
    r = connect_backing(args)
    cached_data = cache_setup(args)
    if args.test == True:
        #test_ttl(r, args)
        test_lru(r, args)
    uvicorn.run(app, host=args.proxy_host, port=args.proxy_port)