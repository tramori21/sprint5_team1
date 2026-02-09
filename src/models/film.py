from typing import Optional
from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float] = None
    persons: Optional[list[str]] = None
