import aiohttp
import pytest

TIMEOUT = aiohttp.ClientTimeout(total=5)

@pytest.mark.asyncio
async def test_films_pagination_params_accept():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get("http://api:8000/api/v1/films/?page[number]=1&page[size]=10") as resp:
            assert resp.status == 200

@pytest.mark.asyncio
async def test_genres_pagination_params_accept():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get("http://api:8000/api/v1/genres/?page[number]=1&page[size]=10") as resp:
            assert resp.status == 200

@pytest.mark.asyncio
async def test_persons_pagination_params_accept():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get("http://api:8000/api/v1/persons/?page[number]=1&page[size]=10") as resp:
            assert resp.status == 200
