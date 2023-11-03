from fastapi import FastAPI
import uvicorn
import time
import redis
from cachetools import TTLCache
import argparse

parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('--host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('--port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=1)
parser.add_argument('-k', '--count', type=int, help='Number of items to cache', default=60)
parser.add_argument('--pw', type=str, nargs='?')
parser.add_argument('-T', '--test', action='store_true', help='Run end-to-end tests')
args = parser.parse_args()


def connect_backing(args): # connect to the redis instance
    try:
        r = redis.Redis(host=args.host, port=args.port, db=0, password=args.pw)
        print(f"Successfully connected to backing Redis")
        return(r)
    except redis.exceptions.AuthenticationError as e: 
        print(f"Redis password required: {e}")

def redis_test_conn(r): #ensure we are connected to the redis instance. this may be unneeded or could be merged with connect_backing
    try:
        response = r.ping()
        if response:
            print("Backing Redis ping successful")
        else:
            print("Unable to connect to Redis instance")
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis instance: {e}")

def redis_data_gen(r, count): # create some test data that just squares the key
    for i in range(count):
        r.set(i, i**2)
    print("Added test data to Redis instance")

def test_ttl(r, args): #ensure key values are getting removed after ttl is up
    sleep_time = int(args.ttl)+1
    initial_caching = get_data('5')
    print(f"Pulled initial value from {initial_caching['source']}")
    second_caching = get_data('5')
    print(f"Pulled second time from {second_caching['source']}")
    time.sleep(sleep_time)
    third_caching = get_data('5')
    print(f"Pulled third time from {third_caching['source']}")
    if third_caching['source'] == 'redis':
        print(f"Cached value removed after {args.ttl} seconds.")
    print(sleep_time)

def test_lru(r):
    print('stop linting lru')

def clean_redis(r):
    print('lint clean')

app = FastAPI()
@app.get('/get_data')
def get_data(key): #pull data from redis or cache if possible
    if not key:
        return ({'error': 'no key parameter'})
    if key in cached_data:
        return ({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'cache'})
    try:
        cached_data.update({key: r.get(key)})
        return ({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'redis'})
    except:
        return ({'error': 'key not found in redis'})
@app.middleware("http") # track the speed of our calls
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
    return response


if __name__ == '__main__':
    r = connect_backing(args)
    cached_data = TTLCache(maxsize=args.count, ttl=args.ttl)
    if args.test == True:
        redis_test_conn(r)
        redis_data_gen(r, 100) #where 100 is the number of entries in the redis db
        test_ttl(r, args)
        test_lru(r)
        clean_redis(r)
    uvicorn.run(app, host='0.0.0.0', port=9999)