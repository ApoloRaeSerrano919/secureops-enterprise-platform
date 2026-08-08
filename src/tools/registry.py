from pydantic import BaseModel, Field

class PrincipalArgs(BaseModel):
    principal: str = Field(min_length=3, max_length=255)

class ServiceArgs(BaseModel):
    service: str = Field(min_length=2, max_length=120)

