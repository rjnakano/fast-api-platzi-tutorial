# Python
from optparse import Option
from typing import Optional

# Pydantic
from pydantic import BaseModel

# FastAPI
from fastapi import FastAPI, Body, Query


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
    name: Optional[str] = Query(default=None, min_length=1, max_length=50),
    age: str = Query(...) # required query parameter
):
    return {name: age}