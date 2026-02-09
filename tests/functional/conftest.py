import aiohttp
import pytest_asyncio

from settings import API_HOST, ES_HOST, REDIS_HOST, REDIS_PORT
from utils import load_data
from wait_for_api import wait_for_api
from wait_for_es import wait_for_es
from wait_for_redis import wait_for_redis


@pytest_asyncio.fixture(scope="session", autouse=True)
async def load_testdata():
    await wait_for_es(ES_HOST)
    await wait_for_redis(REDIS_HOST, REDIS_PORT)
    await wait_for_api(API_HOST)
    await load_data()


@pytest_asyncio.fixture
async def api_client():
    async with aiohttp.ClientSession() as session:
        yield session
