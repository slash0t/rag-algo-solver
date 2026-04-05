from app.domain.models.query import IntermediateQuery, RawQuery
from app.domain.services.enrichment.block import EnrichmentBlock
from app.domain.services.query_enricher import QueryEnricher


class EnrichmentPipeline(QueryEnricher):
    def __init__(self, blocks: list[EnrichmentBlock]) -> None:
        self._blocks = blocks

    async def enrich(self, raw_query: RawQuery) -> str:
        intermediate = IntermediateQuery(
            original_text=raw_query.text,
            enriched_text=raw_query.text,
        )
        for block in self._blocks:
            intermediate = await block.process(intermediate)
        return intermediate.enriched_text
