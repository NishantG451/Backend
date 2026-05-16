from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: int


class TaskUpdate(BaseModel):
    title: str
    description: str
    status: str