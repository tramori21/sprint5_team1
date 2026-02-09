from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.deps.pagination import PaginationParams
from src.models.film import Film
from src.models.person import Person
from src.services.persons import PersonService

router = APIRouter()


@router.get("/", response_model=list[Person], status_code=status.HTTP_200_OK)
async def persons_list(
    request: Request,
    pagination: PaginationParams = Depends(),
) -> list[Person]:
    service = PersonService(request)
    return await service.get_list(
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )


@router.get("/{person_id}", response_model=Person, status_code=status.HTTP_200_OK)
async def person_details(person_id: str, request: Request) -> Person:
    service = PersonService(request)
    person = await service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="person not found")
    return person


@router.get("/{person_id}/film", response_model=list[Film], status_code=status.HTTP_200_OK)
async def person_films(
    person_id: str,
    request: Request,
    pagination: PaginationParams = Depends(),
) -> list[Film]:
    service = PersonService(request)
    return await service.get_films(
        person_id=person_id,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )
