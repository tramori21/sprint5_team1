from elasticsearch import NotFoundError
from fastapi import Request

from src.db.elastic import get_elastic
from src.models.film import Film


class SearchElasticRepository:
    def __init__(self, request: Request):
        self.es = get_elastic(request)

    async def search(self, phrase: str, page_number: int, page_size: int) -> list[Film]:
        try:
            response = await self.es.search(
                index="movies",
                query={"match": {"title": {"query": phrase}}},
                from_=(page_number - 1) * page_size,
                size=page_size,
            )
            return [Film(**hit["_source"]) for hit in response["hits"]["hits"]]
        except NotFoundError:
            return []
