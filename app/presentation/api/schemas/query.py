from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateQueryRequest(BaseModel):
    text: str


class CreateQueryResponse(BaseModel):
    query_id: UUID
    processing_id: UUID
    status: str


class QueryResponse(BaseModel):
    id: UUID
    user_id: UUID
    text: str
    response_text: str | None = None
    created_at: datetime
    responded_at: datetime | None = None


class QueryListItem(BaseModel):
    id: UUID
    text: str
    response_text: str | None = None
    created_at: datetime
    responded_at: datetime | None = None


class QueryPaginatedResponse(BaseModel):
    items: list[QueryListItem]
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1)
