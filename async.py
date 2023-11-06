import asyncio
import aioredis

async def test_redis_proxy():
    r = await aioredis.from_url('redis://localhost:9999')
    result = await r.execute('PING')  # You can replace 'PING' with any valid Redis command.
    print(result)
    r.close()
    await r.wait_closed()

if __name__ == '__main__':
    asyncio.run(test_redis_proxy())