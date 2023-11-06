import redis
import aioredis
from cachetools import TTLCache
import argparse
import asyncio
from asyncio import start_server
#from redis.commands import create_handler, read_response

parser = argparse.ArgumentParser(description='Redis caching proxy')
parser.add_argument('--redis_host', type=str, help='Hostname or IP of backing Redis', default='127.0.0.1')
parser.add_argument('--redis_port', type=str, help='Port of backing Redis', default='6379')
parser.add_argument('--proxy_host', type=str, help='The listening IP of the proxy', default='0.0.0.0')
parser.add_argument('--proxy_port', type=str, help='The listening port of the proxy', default='9999')
parser.add_argument('-t', '--ttl', type=int, help='Cache TTL in seconds', default=10)
parser.add_argument('-k', '--size', type=int, help='Number of items to cache', default=10)
parser.add_argument('--password', type=str, nargs='?')
args = parser.parse_args()
cached_data = TTLCache(maxsize = args.size, ttl = args.ttl)

async def cache_handler(reader, writer):
    r = await aioredis.create_redis(args.redis_host, args.redis_port, password = args.password)
    while True:
        data = await reader.readuntil(b'\r\n') #brn marks the end of redis commands
        command = data.decode().strip()
        if command.startswith('*'):
            num_args = int(command[1:])
            redis_command = await reader.readuntil(b'\r\n')
            for _ in range(num_args):
                arg_length = int(redis_command[1:])
                arg = await reader.readexactly(arg_length + 2)
                redis_command += arg
            if redis_command.startswith(b'$3\r\nGET'):
                key = redis_command.split(b'\r\n')[1]
                if key in cached_data: #pull from cache if possible
                    response = b'$' + str(len(cached_data[key])).encode() + b'\r\n' + cached_data[key] + b'\r\n'
                else: #pull key from redis, store in cache
                    response = await r.execute(redis_command)
                    cached_data[key] = response
            else: #run multiple non get commands
                response = await r.execute(redis_command)
        else: #run single non get command
            response = await r.execute(redis_command)
        writer.write(response)
        await writer.drain()

def redis_data_gen():
    r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0, password=args.password, socket_timeout=1)
    for i in range(100):
        r.set(i, i**2)
    print("Added test data to Redis instance")
     
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(start_server(cache_handler, args.proxy_host, args.proxy_port))
    redis_data_gen()
    loop.run_forever()