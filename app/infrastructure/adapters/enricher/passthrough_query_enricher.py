from app.domain.models.query import RawQuery
from app.domain.services.query_enricher import QueryEnricher


class PassthroughQueryEnricher(QueryEnricher):
    async def enrich(self, raw_query: RawQuery) -> str:
        return raw_query.text
