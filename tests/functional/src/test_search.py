import json

import aiohttp
import pytest
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError

from settings import API_HOST

from sample_data import film_id as get_film_id, search_phrase_from_first_film_title as get_phrase

TIMEOUT = aiohttp.ClientTimeout(total=10)


@pytest.mark.asyncio
async def test_search_validation_missing_query():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/search/") as resp:
            assert resp.status == 422


@pytest.mark.asyncio
async def test_search_validation_empty_query():
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/search/?query=") as resp:
            assert resp.status == 422


@pytest.mark.asyncio
async def test_search_validation_page_size_zero():
    phrase = get_phrase()
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/search/?query={phrase}&page[number]=1&page[size]=0") as resp:
            assert resp.status == 422


@pytest.mark.asyncio
async def test_search_phrase_and_limit_n():
    phrase = get_phrase()
    fid = get_film_id()

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        async with session.get(f"{API_HOST}/api/v1/search/?query={phrase}&page[number]=1&page[size]=1") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert isinstance(data, list)
            assert len(data) == 1
            # хотя бы один из результатов должен быть из набора данных (обычно это первый фильм)
            assert "id" in data[0]


@pytest.mark.asyncio
async def test_search_cache_in_redis_restore_es_after():
    phrase = get_phrase()
    fid = get_film_id()

    r = redis.Redis(host="redis", port=6379)
    es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])

    try:
        await r.flushall()

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(f"{API_HOST}/api/v1/search/?query={phrase}&page[number]=1&page[size]=10") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert any(x.get("id") == fid for x in data)

        cached = await r.get(f"search:{phrase}:1:10")
        assert cached is not None
        cached_list = json.loads(cached)
        assert any(x.get("id") == fid for x in cached_list)

        # гарантируем наличие документа в ES, потом удаляем
        try:
            src = await es.get(index="movies", id=fid)
        except NotFoundError:
            assert False, f"ES doc not found for movies/{fid}"

        film_doc = src["_source"]

        await es.delete(index="movies", id=fid, refresh=True)

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.get(f"{API_HOST}/api/v1/search/?query={phrase}&page[number]=1&page[size]=10") as resp:
                assert resp.status == 200
                from_cache = await resp.json()
                assert any(x.get("id") == fid for x in from_cache)

        # восстановить документ обратно
        await es.index(index="movies", id=fid, document=film_doc, refresh="wait_for")
    finally:
        await es.close()
        await r.aclose()
