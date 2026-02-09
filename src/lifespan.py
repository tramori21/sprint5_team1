from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from redis.asyncio import Redis

from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = AsyncElasticsearch(hosts=[settings.elastic_host])
    r = Redis(host=settings.redis_host, port=settings.redis_port)

    app.state.elasticsearch = es
    app.state.redis = r

    yield

    await r.aclose()
    await es.close()
