from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional


class PlatformCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    url: HttpUrl
    homepage_uri: HttpUrl
    description: Optional[str] = None
    skills_url: HttpUrl


class PlatformUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    homepage_uri: Optional[HttpUrl] = None
    description: Optional[str] = None
    skills_url: Optional[HttpUrl] = None


class SkillCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    platform_id: str
    capabilities: str
    skill_name: Optional[str] = None
    tags: Optional[list[str]] = None
