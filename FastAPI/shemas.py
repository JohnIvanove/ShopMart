from pydantic import BaseModel

class UserBase (BaseModel):
    name: str
    age: int

class User (UserBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True

class UserCreate (UserBase):
    ...
