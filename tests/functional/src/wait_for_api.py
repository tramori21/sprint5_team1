import asyncio
import aiohttp


async def wait_for_api(api_host: str, timeout: int = 60):
    url = api_host.rstrip("/") + "/api/v1/health"
    client_timeout = aiohttp.ClientTimeout(total=2)

    for _ in range(timeout):
        try:
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return
        except Exception:
            pass
        await asyncio.sleep(1)

    raise RuntimeError("API is not available")
