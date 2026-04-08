from datetime import datetime

from app.container import APP_CONTAINER
from app.infrastructure.database.models import ProcessingStatus
from app.presentation.streams.app import broker, kafka_config
from app.presentation.streams.schemas.processing import ProcessingMessage


@broker.subscriber(kafka_config.topic_generate)
async def generate_handler(msg: ProcessingMessage) -> None:
    processing_repo = APP_CONTAINER.processing_repo()
    query_repo = APP_CONTAINER.query_repo()
    composer = APP_CONTAINER.composer()
    llm_client = APP_CONTAINER.llm_client()

    processing = await processing_repo.get(msg.processing_id)

    try:
        prepared = await composer.compose(
            original_text=processing.original_text,
            enriched_text=processing.enriched_text,
            task_context=processing.task_context or "",
        )

        response_text = await llm_client.generate(prepared.text)

        query = await query_repo.get(processing.query_id)
        query.response_text = response_text
        query.responded_at = datetime.utcnow()
        await query_repo.update(query)

        processing.status = ProcessingStatus.COMPLETED
        await processing_repo.update(processing)
    except Exception as e:
        processing.status = ProcessingStatus.FAILED
        processing.error_message = str(e)
        await processing_repo.update(processing)
