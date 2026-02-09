import aiohttp
import pytest

from settings import API_HOST

from sample_data import film_id as get_film_id, person_id_for_first_film as get_person_id

TIMEOUT = aiohttp.ClientTimeout(total=10)


@pytest.mark.asyncio
async def test_person_get_by_id():
    pid = get_person_id()
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/persons/{pid}") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["id"] == pid


@pytest.mark.asyncio
async def test_person_films_contains_first_film():
    pid = get_person_id()
    fid = get_film_id()

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/persons/{pid}/film?page[number]=1&page[size]=10") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert any(x.get("id") == fid for x in data)
