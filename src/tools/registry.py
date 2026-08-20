from pydantic import BaseModel, Field
import httpx

from src.config.settings import settings


class PrincipalArgs(BaseModel):
    principal: str = Field(min_length=3, max_length=255)


