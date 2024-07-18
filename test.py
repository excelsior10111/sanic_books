import redis.asyncio as redis
import asyncio 

async def test():
    client = redis.Redis()
    print(f"Ping successful: {await client.ping()}")
    await client.setex("test", 3600, 'value')
    await client.aclose()

asyncio.run(test())