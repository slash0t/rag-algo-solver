from dependency_injector import containers, providers

from app.infrastructure.adapters.composer.plain_prompt_composer import PlainPromptComposer
from app.infrastructure.adapters.context.plain_task_context_builder import PlainTaskContextBuilder
from app.infrastructure.adapters.enricher.passthrough_query_enricher import PassthroughQueryEnricher
from app.infrastructure.adapters.llm.echo_llm_client import EchoLLMClient
from app.infrastructure.adapters.search.empty_similar_task_searcher import EmptySimilarTaskSearcher
from app.infrastructure.database.repositories.query import SQLQueryRepository
from app.infrastructure.database.repositories.query_processing import SQLQueryProcessingRepository
from app.infrastructure.database.session import create_async_session_factory
from app.settings.postgres import PostgresConfig
from app.settings.yandex_cloud import YandexCloudConfig


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    yandex_cloud_config: providers.Singleton[YandexCloudConfig] = providers.Singleton(YandexCloudConfig)

    postgres_config: providers.Singleton[PostgresConfig] = providers.Singleton(PostgresConfig)

    session_factory = providers.Singleton(
        create_async_session_factory,
        config=postgres_config,
    )

    query_repo: providers.Singleton[SQLQueryRepository] = providers.Singleton(
        SQLQueryRepository,
        session_factory=session_factory,
    )

    processing_repo: providers.Singleton[SQLQueryProcessingRepository] = providers.Singleton(
        SQLQueryProcessingRepository,
        session_factory=session_factory,
    )

    enricher: providers.Singleton[PassthroughQueryEnricher] = providers.Singleton(PassthroughQueryEnricher)

    searcher: providers.Singleton[EmptySimilarTaskSearcher] = providers.Singleton(EmptySimilarTaskSearcher)

    context_builder: providers.Singleton[PlainTaskContextBuilder] = providers.Singleton(PlainTaskContextBuilder)

    composer: providers.Singleton[PlainPromptComposer] = providers.Singleton(PlainPromptComposer)

    llm_client: providers.Singleton[EchoLLMClient] = providers.Singleton(EchoLLMClient)


APP_CONTAINER = AppContainer()
