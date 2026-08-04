from pydantic import BaseModel, Field

class PrincipalArgs(BaseModel):
    principal: str = Field(min_length=3, max_length=255)

