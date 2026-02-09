from fastapi import APIRouter, Depends, Query, Request, status

from src.api.deps.pagination import PaginationParams
from src.models.film import Film
from src.services.search import SearchService

router = APIRouter()


@router.get("/", response_model=list[Film], status_code=status.HTTP_200_OK)
async def search(
    request: Request,
    pagination: PaginationParams = Depends(),
    query: str = Query(..., min_length=1),
) -> list[Film]:
    service = SearchService(request)
    return await service.search(
        phrase=query,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )
