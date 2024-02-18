from pydantic import BaseModel

# Models


class BookCreate(BaseModel):
    title: str
    author: str
    published_year: int


class Book(BaseModel):
    id: int
    title: str
    author: str
    published_year: int
