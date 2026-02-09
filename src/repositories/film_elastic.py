from elasticsearch import NotFoundError
from fastapi import Request

from src.db.elastic import get_elastic
from src.models.film import Film


class FilmElasticRepository:
    def __init__(self, request: Request):
        self.es = get_elastic(request)

    async def get(self, film_id: str) -> Film | None:
        try:
            doc = await self.es.get(index="movies", id=film_id)
            return Film(**doc["_source"])
        except NotFoundError:
            return None

    async def get_list(self, page_number: int, page_size: int) -> list[Film]:
        try:
            response = await self.es.search(
                index="movies",
                query={"match_all": {}},
                from_=(page_number - 1) * page_size,
                size=page_size,
            )
            return [Film(**hit["_source"]) for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []
