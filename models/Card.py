from pydantic import BaseModel, field_validator, Field

class Card(BaseModel):
    title: str = Field(..., min_length=1, )
    description: str = Field(..., min_length=1)
