# Python
from typing import Optional

# Pydantic
from pydantic import BaseModel

# FastAPI
from fastapi import FastAPI, Body, Path, Query


app = FastAPI()

# Models
class Person(BaseModel):
    first_name: str
    last_name: str
    age: int
    hair_color: Optional[str] = None
    is_married: Optional[bool] = None

@app.get("/")
def home():
    return {"Hello":"World"}

# Request and response body
@app.post("/person/new")
def create_person(
    person: Person = Body(...) # required body parameter
):
    return person

# Validations: Query parameters

@app.get("/person/detail")
def show_person(
    name: Optional[str] = Query(
        default=None, 
        min_length=1, 
        max_length=50,
        title="Person Name",
        description="This is the person's fullname. It has to be between 1 and 50 characters"
        ),
    age: int = Query(
        default=...,
        ge=18,
        title="Person Age",
        description="This is the person's age. It's required and has to be greater on equal than 18"
        ) # required query parameter and greater or equal than 18 (ge,gt,le,lt)
):
    return {name: age}

# Validations: Path Parameters
@app.get("/person/detail/{person_id}")
def show_person(
    person_id: int = Path(
        default=...,
        gt=0
        )
):
    return {person_id: f"It exists!"} 