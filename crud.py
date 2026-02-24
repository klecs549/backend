from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import TravelProject, ProjectPlace
from schemas import ProjectCreate, PlaceCreate
import requests

MAX_PLACES = 10


# ---------- PROJECTS ----------

def create_project(db: Session, project: ProjectCreate):
    if len(project.places) > MAX_PLACES:
        raise HTTPException(status_code=400, detail="Max 10 places allowed")

    db_project = TravelProject(
        name=project.name,
        description=project.description,
        start_date=project.start_date,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # add places if provided
    for place in project.places:
        add_place_to_project(db, db_project.id, place)

    return db_project


def delete_project(db: Session, project_id: int):
    project = db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if any(p.visited for p in project.places):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete project with visited places"
        )

    db.delete(project)
    db.commit()


def update_project_completion(project: TravelProject):
    if project.places and all(p.visited for p in project.places):
        project.completed = True

def add_place_to_project(db: Session, project_id: int, place: PlaceCreate):
    project = db.get(TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(project.places) >= MAX_PLACES:
        raise HTTPException(status_code=400, detail="Max 10 places allowed")

    # prevent duplicates
    if any(p.external_id == place.external_id for p in project.places):
        raise HTTPException(status_code=400, detail="Place already added")

    # validate against Art API
    title = validate_artwork(place.external_id)

    db_place = ProjectPlace(
        project_id=project_id,
        external_id=place.external_id,
        title=title,
        notes=place.notes,
    )

    db.add(db_place)
    db.commit()
    db.refresh(db_place)

    return db_place


def update_place(db: Session, project_id: int, place_id: int, payload):
    place = db.get(ProjectPlace, place_id)

    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")

    if payload.notes is not None:
        place.notes = payload.notes

    if payload.visited is not None:
        place.visited = payload.visited

    update_project_completion(place.project)

    db.commit()
    db.refresh(place)

    return place

ART_API_URL = "https://api.artic.edu/api/v1/artworks"


def validate_artwork(external_id: int):
    url = f"{ART_API_URL}/{external_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Artwork not found")

    data = response.json()
    return data["data"]["title"]