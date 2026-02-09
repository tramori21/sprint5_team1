import json

import aiohttp
import pytest
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError

from settings import API_HOST

from sample_data import film_id as get_film_id

TIMEOUT = aiohttp.ClientTimeout(total=10)


@pytest.mark.asyncio
async def test_films_list_limit_n():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/films/?page[number]=1&page[size]=1") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) == 1


@pytest.mark.asyncio
async def test_films_list_validation_page_size_zero():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/films/?page[number]=1&page[size]=0") as resp:
            assert resp.status == 422


@pytest.mark.asyncio
async def test_film_get_by_id():
    fid = get_film_id()
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/films/{fid}") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["id"] == fid


@pytest.mark.asyncio
async def test_film_not_found():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/films/unknown") as resp:
            assert resp.status == 404


@pytest.mark.asyncio
async def test_film_cache_in_redis_restore_es_after():
    fid = get_film_id()

    r = redis.Redis(host="redis", port=6379)
    es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

    try:
        await r.flushall()

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(f"{API_HOST}/api/v1/films/{fid}") as resp:
                assert resp.status == 200
                original = await resp.json()

        cached = await r.get(f"film:{fid}")
        assert cached is not None
        assert json.loads(cached)["id"] == fid

        # гарантируем, что документ реально есть в ES, иначе delete бессмысленен
        try:
            src = await es.get(index="movies", id=fid)
        except NotFoundError:
            assert False, f"ES doc not found for movies/{fid}"

        film_doc = src["_source"]

        await es.delete(index="movies", id=fid, refresh=True)

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(f"{API_HOST}/api/v1/films/{fid}") as resp:
                assert resp.status == 200
                from_cache = await resp.json()

        assert from_cache == original

        # восстановить документ обратно
        await es.index(index="movies", id=fid, document=film_doc, refresh="wait_for")
    finally:
        await es.close()
        await r.aclose()
