from flask import Flask, request, jsonify
import redis
from cachetools import TTLCache
import argparse



def redis_test_conn(r):
    try:
        response = r.ping()
        if response:
            print("Connected to Redis instance")
        else:
            print("Unable to connect to Redis instance")
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis instance: {e}")

def redis_data_gen(r, count):
    for i in range(count):
        r.set(i, i**2)
    print("Added test data to Redis instance")

host = '0.0.0.0' #bind address and port for flask
port = 9999
app = Flask(__name__)
@app.route('/get_data', methods = ['GET'])
def get_data():
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
    parser = argparse.ArgumentParser(description='Redis caching proxy')
    parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis')
    parser.add_argument('--redis_port', type=str, help='Port of backing Redis')
    parser.add_argument('--ttl', type=int, help='Cache TTL in seconds')
    parser.add_argument('--count', type=int, help='Number of items to cache')
    parser.add_argument('--pw', type=str, )
    args = parser.parse_args()

    r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0, password=args.pw)
    cached_data = TTLCache(maxsize=args.count, ttl=args.ttl)
    redis_test_conn(r)
    redis_data_gen(r, 100)
    app.run(host=host, debug=True, port=port)