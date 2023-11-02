from flask import Flask, request, jsonify
import redis
from cachetools import TTLCache
import argparse

redis_host = '192.168.1.18' #redis instance
redis_port = 6379
redis_pw = 'rescale'
ttl = 10 #Cache expiry time in seconds
k = 100 #Cache capacity (number of keys)
host = '0.0.0.0' #bind address and port for flask
port = 9999
cached_data = TTLCache(maxsize=k, ttl=ttl)
app = Flask(__name__)
r = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_pw)
try:
    response = r.ping()
    if response:
        print("Connected to Redis instance")
    else:
        print("Unable to connect to Redis instance")
except redis.exceptions.ConnectionError as e:
    print(f"Failed to connect to Redis instance: {e}")

def redis_test_data(r, count):
    for i in range(count):
        r.set(i, i**2)
    print("Added test data to Redis instance")

count = 100
redis_test_data(r, count)

@app.route('/get_data', methods = ['GET'])
def get_data():
    key = request.args.get('key')
    if not key:
        return jsonify({'error': 'No key parameter'}), 400
    
    if key in cached_data:
        return jsonify({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'cache'})
    cached_data.update({key: r.get(key)})
    return jsonify({'key': key, 'data': cached_data[key].decode('utf-8'), 'source': 'redis'})



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Redis caching proxy')
    parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis')
    parser.add_argument('--redis_port', type=str, help='Port of backing Redis')
    parser.add_argument('--ttl', type=int, help='Cache TTL in seconds')
    parser.add_argument('--count', type=float, help='Number of items to cache')
    args = parser.parse_args()
    app.run(host=host, debug=True, port=port)