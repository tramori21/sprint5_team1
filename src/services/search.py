import json
from fastapi import Request

from src.db.redis import get_redis
from src.models.film import Film
from src.repositories.search_elastic import SearchElasticRepository


class SearchService:
    def __init__(self, request: Request):
        self.repo = SearchElasticRepository(request)
        self.redis = get_redis(request)

    async def search(self, phrase: str, page_number: int, page_size: int) -> list[Film]:
        key = f"search:{phrase}:{page_number}:{page_size}"

        cached = await self.redis.get(key)
        if cached:
            return [Film(**x) for x in json.loads(cached)]

        items = await self.repo.search(phrase, page_number, page_size)

        await self.redis.set(
            key,
            json.dumps([x.model_dump() for x in items]),
            ex=60,
        )
        return items
