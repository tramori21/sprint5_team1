from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.deps.pagination import PaginationParams
from src.models.genre import Genre
from src.services.genres import GenreService

router = APIRouter()


@router.get("/", response_model=list[Genre], status_code=status.HTTP_200_OK)
async def genres_list(
    request: Request,
    pagination: PaginationParams = Depends(),
) -> list[Genre]:
    service = GenreService(request)
    return await service.get_list(
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )


@router.get("/{genre_id}", response_model=Genre, status_code=status.HTTP_200_OK)
async def genre_details(genre_id: str, request: Request) -> Genre:
    service = GenreService(request)
    genre = await service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="genre not found")
    return genre
