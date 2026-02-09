from elasticsearch import NotFoundError
from fastapi import Request

from src.db.elastic import get_elastic
from src.models.film import Film
from src.models.person import Person


class PersonElasticRepository:
    def __init__(self, request: Request):
        self.es = get_elastic(request)

    async def get(self, person_id: str) -> Person | None:
        try:
            doc = await self.es.get(index="persons", id=person_id)
            return Person(**doc["_source"])
        except NotFoundError:
            return None

    async def get_list(self, page_number: int, page_size: int) -> list[Person]:
        try:
            response = await self.es.search(
                index="persons",
                query={"match_all": {}},
                from_=(page_number - 1) * page_size,
                size=page_size,
            )
            return [Person(**hit["_source"]) for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []

    async def get_films(self, person_id: str, page_number: int, page_size: int) -> list[Film]:
        try:
            response = await self.es.search(
                index="movies",
                query={"terms": {"persons": [person_id]}},
                from_=(page_number - 1) * page_size,
                size=page_size,
            )
            return [Film(**hit["_source"]) for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []
