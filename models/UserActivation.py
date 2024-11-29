from pydantic import BaseModel, field_validator, EmailStr, Field
from typing import Optional
import re

class UserActivation(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)