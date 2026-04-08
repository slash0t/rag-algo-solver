from app.container import APP_CONTAINER
from app.domain.models.query import RawQuery
from app.infrastructure.database.models import ProcessingStatus
from app.presentation.streams.app import broker, kafka_config
from app.presentation.streams.schemas.processing import ProcessingMessage


@broker.subscriber(kafka_config.topic_enrich)
async def enrich_handler(
    msg: ProcessingMessage,
) -> None:
    processing_repo = APP_CONTAINER.processing_repo()
    enricher = APP_CONTAINER.enricher()

    processing = await processing_repo.get(msg.processing_id)

    try:
        enriched_text = await enricher.enrich(
            RawQuery(text=processing.original_text),
        )

        processing.enriched_text = enriched_text
        processing.status = ProcessingStatus.SEARCHING
        await processing_repo.update(processing)

        await broker.publish(
            ProcessingMessage(processing_id=processing.id),
            topic=kafka_config.topic_search,
        )
    except Exception as e:
        processing.status = ProcessingStatus.FAILED
        processing.error_message = str(e)
        await processing_repo.update(processing)
