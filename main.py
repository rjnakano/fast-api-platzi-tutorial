# Python
from doctest import Example
from optparse import Option
from typing import Optional
from enum import Enum
from utils.errors import *

# Pydantic
from pydantic import BaseModel, EmailStr, PaymentCardNumber, HttpUrl
from pydantic import Field, validator
# FastAPI
from fastapi import FastAPI, UploadFile, status, HTTPException
from fastapi import Body, File, Path, Query, Form, Header, Cookie

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
    status_code=status.HTTP_200_OK,
    tags=["Home"]
)
def home():
    return {"Hello":"World"}

# Request and response body
@app.post(
    path = "/person/new", 
    response_model = PersonOut,
    status_code = status.HTTP_201_CREATED,
    tags=["Persons"],
    summary="Create person in the app"
)
def create_person(
    person: Person = Body(...) # required body parameter
):
    '''
    <h2>Create Person (create_person)</h2>
    
    This path operation creates a person in the app and saves the information in the database
    
    Parameters:
    - Request body parameter:
        - **person: Person** -> A person with first name, last name, age, hair color and marital status
    
    Returns a person model with first name, last name, age, hair color and marital status
    '''
    return person

# Validations: Query parameters
@app.get(
    path="/person/detail",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
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

persons = [1,2,3,4,5]

# Validations: Path Parameters
@app.get(
    path="/person/detail/{person_id}",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
)
def show_person(
    person_id: int = Path(
        default=...,
        gt=0,
        example=12
        )
):
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="¡This person doesn't exist!"
        )
    return {person_id: f"It exists!"} 

# Validations: Request Body
@app.put(
    path="/person/{person_id}",
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
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

# Forms
@app.post(
    path="/login",
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
)
def login(
    username: str = Form(...),
    password:str = Form(...)
):
    return LoginOut(username=username) # The class must be instanciated to be able to cast it to a JSON format. Otherwise, it will fail

# Cookies and header parameters    
@app.post(
    path="/contact",
    status_code=status.HTTP_200_OK,
    tags=["Utils"]
)
def contact(
    first_name:str = Form(
        ...,
        max_length=20,
        min_length=1
    ),
    last_name:str = Form(
        ...,
        max_length=20,
        min_length=1
    ),
    email : EmailStr = Form(...),
    message: str = Form(
        ...,
        min_length=20
    ),
    user_agent: Optional[str]= Header(default=None),
    ads: Optional[str] = Cookie(default=None)
):
    return user_agent

# Files
@app.post(
    path="/post-image",
    tags=["Utils"]
)
def post_image(
    image: UploadFile = File(...)
):
    return {
        "Filaname": image.filename,
        "Format": image.content_type,
        "Size(kb)": round(len(image.file.read())/1024,ndigits=2)
    }