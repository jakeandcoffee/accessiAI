from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class WebsiteCreate(BaseModel):
    name: str
    url: HttpUrl


class WebsiteUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None


class WebsiteResponse(BaseModel):
    id: UUID
    name: str
    url: str
    created_at: datetime
    latest_score: float | None = None
    last_scanned: datetime | None = None

    model_config = {"from_attributes": True}
