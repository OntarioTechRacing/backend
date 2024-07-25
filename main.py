from enum import Enum
from typing import List, Annotated
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import shutil

import models
from database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = "./uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


class UserBase(BaseModel):
    username: str
    email: str
    name: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class JobStatusEnum(str, Enum):
    completed = "completed"
    running = "running"
    incomplete = "incomplete"


class JobBase(BaseModel):
    filename: str
    description: str
    status: JobStatusEnum
    progress: int


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    status: JobStatusEnum
    progress: int


class JobResponse(JobBase):
    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
db_depend = Annotated[Session, Depends(get_db)]


@app.post("/signup/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserBase])
async def get_users(db: db_dependency):
    return db.query(models.User).all()


@app.post("/login/")
async def login(user: UserLogin, db: db_dependency):
    db_user = (
        db.query(models.User)
        .filter(models.User.username == user.username)
        .first()
    )
    if db_user is None or db_user.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"msg": "Login successful"}


@app.delete("/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(username: str, db: db_dependency):
    db_user = (
        db.query(models.User).filter(models.User.username == username).first()
    )
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(db_user)
    db.commit()
    return {"msg": "User deleted successfully"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/jobs/", response_model=List[JobResponse])
async def get_jobs(db: db_depend):
    return db.query(models.Job).all()


@app.put("/jobs/{filename}", response_model=JobResponse)
async def update_job(filename: str, job: JobUpdate, db: db_depend):
    db_job = (db.query(models.Job)
              .filter(models.Job.filename == filename)
              .first())
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    db_job.status = job.status
    db_job.progress = job.progress
    db.commit()
    db.refresh(db_job)
    return db_job


@app.post("/jobs/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, db: db_depend):
    db_job = models.Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.delete("/jobs/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(filename: str, db: Session = Depends(get_db)):
    db_job = db.query(models.Job).filter(models.Job.filename == filename).first()
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"msg": "Job deleted successfully"}


@app.post("/FileUpload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}
