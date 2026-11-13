from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

MAX_PAGES_PER_WEBSITE = 50


class WebsiteCreate(BaseModel):
    name: str
    url: HttpUrl
    page_urls: list[HttpUrl] = Field(default_factory=list, max_length=MAX_PAGES_PER_WEBSITE)


class WebsiteUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    page_urls: list[HttpUrl] | None = Field(default=None, max_length=MAX_PAGES_PER_WEBSITE)


class WebsiteResponse(BaseModel):
    id: UUID
    name: str
    url: str
    page_urls: list[str] = []
    created_at: datetime
    latest_score: float | None = None
    last_scanned: datetime | None = None

    model_config = {"from_attributes": True}
