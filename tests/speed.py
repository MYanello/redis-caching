import time
import requests

ttl = 1
proxy = '127.0.0.1:9999'
redis = '192.168.1.18:6379'
tests = 9999
def max_sync_speed(proxy, tests):
    results = []
    for i in range(tests):
        key = rand(0,100)
        start_time = time.time()
        requests.get(f"{proxy}/get_data?key=10)")
        results.append(time.time()-start_time)


if __name__ == '__main__':
    max_sync_speed(proxy, tests)