from pydantic import BaseModel, field_validator, Field, EmailStr
from utils.globalf import validate_sql_injection
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(...,  min_length=6, max_length=200)
    firstname: str = Field(..., min_length=2, max_length=50, pattern=r'^[a-zA-ZÀ-ÿ\s]+$')
    lastname: str = Field(...,  min_length=2, max_length=50, pattern=r'^[a-zA-ZÀ-ÿ\s]+$')

    @field_validator('password')
    def password_validation(cls, value):
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[\W_]', value):  # \W matches any non-word character
            raise ValueError('Password must contain at least one special character')
        if re.search(r'(012|123|234|345|456|567|678|789|890)', value):
            raise ValueError('Password must not contain a sequence of numbers')
        return value

    @field_validator('firstname', 'lastname')
    def name_validation(cls, value):
        if validate_sql_injection(value):
            raise ValueError('Invalid name')
        return value