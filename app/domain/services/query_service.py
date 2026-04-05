from app.domain.models.query import QueryResponse, RawQuery
from app.domain.services.llm_client import LLMClient
from app.domain.services.prompt_composer import PromptComposer
from app.domain.services.query_enricher import QueryEnricher
from app.domain.services.similar_task_searcher import SimilarTaskSearcher
from app.domain.services.task_context_builder import TaskContextBuilder


class QueryService:
    def __init__(
        self,
        enricher: QueryEnricher,
        searcher: SimilarTaskSearcher,
        context_builder: TaskContextBuilder,
        composer: PromptComposer,
        llm_client: LLMClient,
    ) -> None:
        self._enricher = enricher
        self._searcher = searcher
        self._context_builder = context_builder
        self._composer = composer
        self._llm_client = llm_client

    async def process(self, raw_query: RawQuery) -> QueryResponse:
        enriched_text = await self._enricher.enrich(raw_query)
        similar_tasks = await self._searcher.search(enriched_text)
        task_context = await self._context_builder.build(similar_tasks)
        prepared = await self._composer.compose(
            original_text=raw_query.text,
            enriched_text=enriched_text,
            task_context=task_context,
        )
        result = await self._llm_client.generate(prepared.text)
        return QueryResponse(text=result)
