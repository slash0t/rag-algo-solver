from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam, status

from app.container import APP_CONTAINER
from app.infrastructure.database.models import (
    ProcessingStatus,
    Query,
    QueryProcessing,
    User,
)
from app.presentation.api.dependencies.auth import get_current_user
from app.presentation.api.schemas.query import (
    CreateQueryRequest,
    CreateQueryResponse,
    QueryListItem,
    QueryPaginatedResponse,
    QueryResponse,
)
from app.presentation.api.schemas.task import SimilarTaskResponse
from app.presentation.streams.schemas.processing import ProcessingMessage

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("", response_model=CreateQueryResponse)
async def create_query(
    request: CreateQueryRequest,
    current_user: User = Depends(get_current_user),
) -> CreateQueryResponse:
    query_repo = APP_CONTAINER.query_repo()
    processing_repo = APP_CONTAINER.processing_repo()
    publisher = APP_CONTAINER.publisher()
    kafka_config = APP_CONTAINER.kafka_config()

    query = Query(
        user_id=current_user.id,
        text=request.text,
    )
    query = await query_repo.create(query)

    processing = QueryProcessing(
        query_id=query.id,
        original_text=request.text,
        status=ProcessingStatus.PENDING,
    )
    processing = await processing_repo.create(processing)

    await publisher.publish(
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


@router.get("", response_model=QueryPaginatedResponse)
async def list_queries(
    current_user: User = Depends(get_current_user),
    page: int = QueryParam(default=1, ge=1),
    size: int = QueryParam(default=10, ge=1, le=100),
) -> QueryPaginatedResponse:
    query_repo = APP_CONTAINER.query_repo()

    offset = (page - 1) * size
    queries, total = await query_repo.list_by_user(current_user.id, offset, size)

    return QueryPaginatedResponse(
        items=[
            QueryListItem(
                id=q.id,
                text=q.text,
                response_text=q.response_text,
                created_at=q.created_at,
                responded_at=q.responded_at,
            )
            for q in queries
        ],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: UUID,
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    query_repo = APP_CONTAINER.query_repo()

    query = await query_repo.get(query_id)
    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    if query.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return QueryResponse(
        id=query.id,
        user_id=query.user_id,
        text=query.text,
        response_text=query.response_text,
        created_at=query.created_at,
        responded_at=query.responded_at,
    )


@router.get("/{query_id}/similar-tasks", response_model=list[SimilarTaskResponse])
async def get_similar_tasks(
    query_id: UUID,
    current_user: User = Depends(get_current_user),
) -> list[SimilarTaskResponse]:
    query_repo = APP_CONTAINER.query_repo()

    query = await query_repo.get_with_similar_tasks(query_id)
    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    if query.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return [
        SimilarTaskResponse(
            id=task.id,
            title=task.title,
            task_url=task.task_url,
            solution_url=task.solution_url,
        )
        for task in query.similar_tasks
    ]
