from uuid import UUID

from pydantic import BaseModel


class ProcessingMessage(BaseModel):
    processing_id: UUID
