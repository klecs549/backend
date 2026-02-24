from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date



class PlaceBase(BaseModel):
    external_id: int
    title: str


class PlaceCreate(PlaceBase):
    notes: Optional[str] = None


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None


class PlaceOut(PlaceBase):
    id: int
    notes: Optional[str]
    visited: bool

    class Config:
        from_attributes = True


# ---------- Project Schemas ----------

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: Optional[List[PlaceCreate]] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    completed: bool
    places: List[PlaceOut]

    class Config:
        from_attributes = True