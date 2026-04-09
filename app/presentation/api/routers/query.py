from fastapi import APIRouter

from app.container import APP_CONTAINER
from app.infrastructure.database.models import (
    ProcessingStatus,
    Query,
    QueryProcessing,
)
from app.presentation.api.schemas.query import CreateQueryRequest, CreateQueryResponse
from app.presentation.streams.schemas.processing import ProcessingMessage

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("", response_model=CreateQueryResponse)
async def create_query(
    request: CreateQueryRequest,
) -> CreateQueryResponse:
    query_repo = APP_CONTAINER.query_repo()
    processing_repo = APP_CONTAINER.processing_repo()
    broker = APP_CONTAINER.broker()
    kafka_config = APP_CONTAINER.kafka_config()

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
