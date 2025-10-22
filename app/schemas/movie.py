from pydantic import BaseModel
from typing import Optional


class MovieCreate(BaseModel):
    title: str
    description: Optional[str] = None
    poster_url: Optional[str] = None
    genre: str
    duration_minutes: int


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    genre: Optional[str] = None
    duration_minutes: Optional[int] = None


class MovieResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    poster_url: Optional[str]
    genre: str
    duration_minutes: int

    class Config:
        from_attributes = True
