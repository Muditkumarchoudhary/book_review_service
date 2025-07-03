from pydantic import BaseModel, ConfigDict, Field
from typing import List

class ReviewCreate(BaseModel):
    reviewer: str
    comment: str

class ReviewOut(ReviewCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookCreate(BaseModel):
    title: str
    author: str

class BookOut(BookCreate):
    id: int
    reviews: List[ReviewOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
