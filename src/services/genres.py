import json
from fastapi import Request

from src.db.redis import get_redis
from src.models.genre import Genre
from src.repositories.genre_elastic import GenreElasticRepository


class GenreService:
    def __init__(self, request: Request):
        self.repo = GenreElasticRepository(request)
        self.redis = get_redis(request)

    async def get_by_id(self, genre_id: str) -> Genre | None:
        key = f"genre:{genre_id}"
        cached = await self.redis.get(key)
        if cached:
            return Genre(**json.loads(cached))

        genre = await self.repo.get(genre_id)
        if genre:
            await self.redis.set(key, json.dumps(genre.model_dump()), ex=60)
        return genre

    async def get_list(self, page_number: int, page_size: int) -> list[Genre]:
        key = f"genres:{page_number}:{page_size}"
        cached = await self.redis.get(key)
        if cached:
            return [Genre(**x) for x in json.loads(cached)]

        genres = await self.repo.get_list(page_number, page_size)
        await self.redis.set(key, json.dumps([g.model_dump() for g in genres]), ex=60)
        return genres
