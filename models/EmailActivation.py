from pydantic import BaseModel, EmailStr

class EmailActivation(BaseModel):
    email: EmailStr
