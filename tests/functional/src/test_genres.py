import aiohttp
import pytest

from settings import API_HOST


TIMEOUT = aiohttp.ClientTimeout(total=5)


@pytest.mark.asyncio
async def test_genres_list():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/genres/") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) >= 2


@pytest.mark.asyncio
async def test_genre_get_by_id():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/genres/genre-1") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["id"] == "genre-1"
            assert data["name"] == "Action"
