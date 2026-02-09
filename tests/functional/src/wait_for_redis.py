import asyncio
import redis.asyncio as redis


async def wait_for_redis(host: str, port: int, timeout: int = 30):
    client = redis.Redis(host=host, port=port)
    for _ in range(timeout):
        try:
            if await client.ping():
                await client.aclose()
                return
        except Exception:
            pass
        await asyncio.sleep(1)
    await client.aclose()
    raise RuntimeError("Redis is not available")
