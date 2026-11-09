from pydantic import BaseModel, ConfigDict

class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    author: str
    isbn: str
    is_available: bool
    id: int 

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str