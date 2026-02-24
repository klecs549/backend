import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import Base, engine, get_db
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Planner API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/projects", response_model=schemas.ProjectOut)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)


@app.get("/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.TravelProject).all()


@app.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.TravelProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    crud.delete_project(db, project_id)
    return {"detail": "Project deleted"}

@app.post("/projects/{project_id}/places", response_model=schemas.PlaceOut)
def add_place(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)):
    return crud.add_place_to_project(db, project_id, place)


@app.get("/projects/{project_id}/places", response_model=list[schemas.PlaceOut])
def list_places(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.ProjectPlace).filter_by(project_id=project_id).all()


@app.get("/projects/{project_id}/places/{place_id}",response_model=schemas.PlaceOut)
def get_place(project_id: int,place_id: int,db: Session = Depends(get_db),):
    place = db.get(models.ProjectPlace, place_id)
    if not place or place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found")
    return place

@app.patch("/projects/{project_id}/places/{place_id}",response_model=schemas.PlaceOut)
def update_place(project_id: int,place_id: int,payload: schemas.PlaceUpdate,db: Session = Depends(get_db)):
    return crud.update_place(db, project_id, place_id, payload)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
