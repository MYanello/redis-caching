from flask import Flask, request, jsonify
import time
import redis
from cachetools import TTLCache
import argparse

parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('-h', '--redis_host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('-p', --redis_port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=60)
parser.add_argument('-k', '--count', type=int, help='Number of items to cache', default=60)
parser.add_argument('-w', '--pw', type=str, nargs='?')
parser.add_argument('-T', '--test', action='store_true', help='Run end-to-end tests')
args = parser.parse_args()

def connect_backing(args): # connect to the redis instance
    try:
        r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0, password=args.pw)
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

def redis_data_gen(r, count):
    for i in range(count):
        r.set(i, i**2)
    print("Added test data to Redis instance")

port = 9999
app = Flask(__name__)
@app.route('/get_data', methods = ['GET'])
def get_data():
    #time.sleep(5)
    key = request.args.get('key')
    if not key:
        return jsonify({'error': 'no key parameter'}), 400
    
    if key in cached_data:
        return jsonify({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'cache'})
    try:
        cached_data.update({key: r.get(key)})
        return jsonify({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'redis'})
    except:
        return jsonify({'error': 'key not found in redis'})



if __name__ == '__main__':
    r = connect_backing(args)
    cached_data = TTLCache(maxsize=args.count, ttl=args.ttl)
    if args.test == True:
        redis_test_conn(r)
        redis_data_gen(r, 100) #where 100 is the number of entries in the redis db
    app.run(host='0.0.0.0', debug=True, port=port)