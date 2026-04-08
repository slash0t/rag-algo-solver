from uuid import UUID

from pydantic import BaseModel


class CreateQueryRequest(BaseModel):
    text: str


class CreateQueryResponse(BaseModel):
    query_id: UUID
    processing_id: UUID
    status: str
