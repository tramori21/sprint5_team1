from elasticsearch import NotFoundError
from fastapi import Request

from src.db.elastic import get_elastic
from src.models.genre import Genre


class GenreElasticRepository:
    def __init__(self, request: Request):
        self.es = get_elastic(request)

    async def get(self, genre_id: str) -> Genre | None:
        try:
            response = await self.es.get(index="genres", id=genre_id)
            return Genre(**response["_source"])
        except NotFoundError:
            return None

    async def get_list(self, page_number: int, page_size: int) -> list[Genre]:
        try:
            response = await self.es.search(
                index="genres",
                query={"match_all": {}},
                from_=(page_number - 1) * page_size,
                size=page_size,
            )
            return [Genre(**hit["_source"]) for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []
