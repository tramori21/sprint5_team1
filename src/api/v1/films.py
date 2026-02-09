from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.deps.pagination import PaginationParams
from src.models.film import Film
from src.services.films import FilmService

router = APIRouter()


@router.get("/", response_model=list[Film], status_code=status.HTTP_200_OK)
async def films_list(
    request: Request,
    pagination: PaginationParams = Depends(),
) -> list[Film]:
    service = FilmService(request)
    return await service.get_list(
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )


@router.get("/{film_id}", response_model=Film, status_code=status.HTTP_200_OK)
async def film_details(film_id: str, request: Request) -> Film:
    service = FilmService(request)
    film = await service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="film not found")
    return film
