import json
from fastapi import Request

from src.db.redis import get_redis
from src.models.film import Film
from src.models.person import Person
from src.repositories.person_elastic import PersonElasticRepository


class PersonService:
    def __init__(self, request: Request):
        self.repo = PersonElasticRepository(request)
        self.redis = get_redis(request)

    async def get_by_id(self, person_id: str) -> Person | None:
        key = f"person:{person_id}"
        cached = await self.redis.get(key)
        if cached:
            return Person(**json.loads(cached))

        person = await self.repo.get(person_id)
        if person:
            await self.redis.set(key, json.dumps(person.model_dump()), ex=60)
        return person

    async def get_list(self, page_number: int, page_size: int) -> list[Person]:
        key = f"persons:{page_number}:{page_size}"
        cached = await self.redis.get(key)
        if cached:
            return [Person(**x) for x in json.loads(cached)]

        persons = await self.repo.get_list(page_number, page_size)
        await self.redis.set(key, json.dumps([p.model_dump() for p in persons]), ex=60)
        return persons

    async def get_films(self, person_id: str, page_number: int, page_size: int) -> list[Film]:
        key = f"person_films:{person_id}:{page_number}:{page_size}"
        cached = await self.redis.get(key)
        if cached:
            return [Film(**x) for x in json.loads(cached)]

        films = await self.repo.get_films(person_id, page_number, page_size)
        await self.redis.set(key, json.dumps([f.model_dump() for f in films]), ex=60)
        return films
