# Python
from doctest import Example
from optparse import Option
from typing import Optional
from enum import Enum
from utils.errors import *

# Pydantic
from pydantic import BaseModel, Field, EmailStr, PaymentCardNumber, HttpUrl, validator
 
# FastAPI
from fastapi import FastAPI, Body, Path, Query, status, Form

app = FastAPI()

# Models
class HairColor(Enum):
    white = "white"
    brown = "brown"
    black = "black"
    blonde = "blonde"
    red = "red"

# Creating a new class to inheret from and avoid possible errors.
class PersonBase(BaseModel):
    first_name: str = Field(
        default=...,
        min_length=1,
        max_length=50)
    last_name: str = Field(
        default=...,
        min_length=1,
        max_length=50
        )
    age: int = Field(
        ...,
        gt=0,
        le=115
        )
    hair_color: Optional[HairColor] = Field(default=None)
    is_married: Optional[bool] = Field(default=None) 
    email: EmailStr = Field(default=None)
    credit_card: Optional[PaymentCardNumber] = Field(default=None)
    url: Optional[HttpUrl] = Field(default=None)
    facebook_url: Optional[HttpUrl] = Field(None)
    
    
    class Config:
        schema_extra = {
            "example":{
                "first_name": "Ryuma",
                "last_name": "Nakano",
                "age": 37,
                "hair_color": "brown",
                "is_married": True,
                "email": "ryuma@nakasan.co",
                "password": "admin123",
                "created_at": "2022/06/07 13:11:20"
            },
            "Lorena":{
                "first_name": "Lorena",
                "last_name": "Sanchez",
                "age": 30,
                "hair_color": "blonde",
                "is_married": False,
                "email": "lorena@nakasan.co"
            }
        }
    
    @validator('facebook_url')
    def check_facebook_url(cls, v):
        if v is None:
            return v
        
        if v.host != "facebook.com" or v.scheme != 'https':
            raise FacebookUrlDomainError()   
        
        if v.path is None or len(v.path)<2: 
            raise FacebookUrlProfileError()
        
        return v
    
class Person(PersonBase):
    password: str = Field(..., min_length=8)
    
class PersonOut(PersonBase):
    pass    
    
class Location(BaseModel):
    city: str = Field(
        ..., 
        min_length=1, 
        max_length=20,
        example="Clearwater"
        )
    state: str = Field(
        ..., 
        min_length=2, 
        max_length=20,
        example="FL"
        )
    country: str = Field(
        ..., 
        min_length=1, 
        max_length=20,
        example="United States"
        )   

class LoginOut(BaseModel):
    username : str = Field(..., max_length=20, example="rnakano")
    message : str = Field(default="Login Successful!", description="Description message")

@app.get(
    path="/",
    status_code=status.HTTP_200_OK
)
def home():
    return {"Hello":"World"}

# Request and response body
@app.post(
    path = "/person/new", 
    response_model = PersonOut,
    status_code = status.HTTP_201_CREATED
)
def create_person(
    person: Person = Body(...) # required body parameter
):
    return person

# Validations: Query parameters
@app.get(
    path="/person/detail",
    status_code=status.HTTP_200_OK
)
def show_person(
    name: Optional[str] = Query(
        default=None, 
        min_length=1, 
        max_length=50,
        title="Person Name",
        description="This is the person's fullname. It has to be between 1 and 50 characters",
        example="Lorena"
        ),
    age: int = Query(
        default=...,
        ge=18,
        title="Person Age",
        description="This is the person's age. It's required and has to be greater on equal than 18",
        example="30"
        ) # required query parameter and greater or equal than 18 (ge,gt,le,lt)
):
    return {name: age}

# Validations: Path Parameters
@app.get(
    path="/person/detail/{person_id}",
    status_code=status.HTTP_200_OK
)
def show_person(
    person_id: int = Path(
        default=...,
        gt=0,
        example=12
        )
):
    return {person_id: f"It exists!"} 

# Validations: Request Body
@app.put(
    path="/person/{person_id}",
    status_code=status.HTTP_200_OK
)
def update_person(
    person_id: int = Path(
        ...,
        title="Person ID",
        description="This is the person ID",
        gt=0,
        example=18
        ),
    person: Person = Body(...),
    location: Location = Body(...)
):
    results = person.dict()
    results.update(location.dict())
    return results

@app.post(
    path="/login",
    response_model=LoginOut,
    status_code=status.HTTP_200_OK
)
def login(
    username: str = Form(...),
    password:str = Form(...)
):
    return LoginOut(username=username) # The class must be instanciated to be able to cast it to a JSON format. Otherwise, it will fail
    