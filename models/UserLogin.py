from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
import re

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    def password_validation(cls, value):
        if len(value) < 6:
            raise ValueError('Password must be at least 6 characters long')

        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[\W_]', value):  # \W matches any non-word character
            raise ValueError('Password must contain at least one special character')

        if re.search(r'(012|123|234|345|456|567|678|789|890)', value):
            raise ValueError('Password must not contain a sequence of numbers')

        return value