from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"