from fastapi import APIRouter

from src.api.v1.films import router as films_router
from src.api.v1.genres import router as genres_router
from src.api.v1.persons import router as persons_router
from src.api.v1.search import router as search_router

api_router = APIRouter()

api_router.include_router(films_router, prefix="/films", tags=["films"])
api_router.include_router(genres_router, prefix="/genres", tags=["genres"])
api_router.include_router(persons_router, prefix="/persons", tags=["persons"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
