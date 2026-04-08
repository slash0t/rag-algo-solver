from fastapi import APIRouter, Depends

from app.container import APP_CONTAINER
from app.domain.repositories.query import QueryRepository
from app.domain.repositories.query_processing import QueryProcessingRepository
from app.infrastructure.database.models import (
    ProcessingStatus,
    Query,
    QueryProcessing,
)
from app.presentation.api.schemas.query import CreateQueryRequest, CreateQueryResponse
from app.presentation.streams.app import broker, kafka_config
from app.presentation.streams.schemas.processing import ProcessingMessage

router = APIRouter(prefix="/queries", tags=["queries"])


def get_query_repo() -> QueryRepository:
    return APP_CONTAINER.query_repo()


def get_processing_repo() -> QueryProcessingRepository:
    return APP_CONTAINER.processing_repo()


@router.post("", response_model=CreateQueryResponse)
async def create_query(
    request: CreateQueryRequest,
    query_repo: QueryRepository = Depends(get_query_repo),
    processing_repo: QueryProcessingRepository = Depends(get_processing_repo),
) -> CreateQueryResponse:
    query = Query(
        user_id=None,
        text=request.text,
    )
    query = await query_repo.create(query)

    processing = QueryProcessing(
        query_id=query.id,
        original_text=request.text,
        status=ProcessingStatus.PENDING,
    )
    processing = await processing_repo.create(processing)

    await broker.publish(
        ProcessingMessage(processing_id=processing.id).model_dump(mode="json"),
        topic=kafka_config.topic_enrich,
    )

    processing.status = ProcessingStatus.ENRICHING
    await processing_repo.update(processing)

    return CreateQueryResponse(
        query_id=query.id,
        processing_id=processing.id,
        status=str(processing.status),
    )
