import aiohttp
import pytest

TIMEOUT = aiohttp.ClientTimeout(total=5)

@pytest.mark.asyncio
async def test_person_films_ok_or_empty():
    # person-1 есть в тест-данных
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get("http://api:8000/api/v1/persons/person-1/film") as resp:
            assert resp.status == 200
