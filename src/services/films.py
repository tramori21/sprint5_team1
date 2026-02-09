import json
from fastapi import Request

from src.db.redis import get_redis
from src.models.film import Film
from src.repositories.film_elastic import FilmElasticRepository


class FilmService:
    def __init__(self, request: Request):
        self.repo = FilmElasticRepository(request)
        self.redis = get_redis(request)

    async def get_by_id(self, film_id: str) -> Film | None:
        key = f"film:{film_id}"
        cached = await self.redis.get(key)
        if cached:
            return Film(**json.loads(cached))

        film = await self.repo.get(film_id)
        if film:
            await self.redis.set(key, json.dumps(film.model_dump()), ex=60)
        return film

    async def get_list(self, page_number: int, page_size: int) -> list[Film]:
        key = f"films:{page_number}:{page_size}"
        cached = await self.redis.get(key)
        if cached:
            return [Film(**x) for x in json.loads(cached)]

        films = await self.repo.get_list(page_number, page_size)
        await self.redis.set(key, json.dumps([f.model_dump() for f in films]), ex=60)
        return films
