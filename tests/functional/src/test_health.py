import aiohttp
import pytest

from settings import API_HOST


TIMEOUT = aiohttp.ClientTimeout(total=5)


@pytest.mark.asyncio
async def test_healthcheck():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/health") as resp:
            assert resp.status == 200
