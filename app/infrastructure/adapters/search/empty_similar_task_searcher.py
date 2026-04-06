from app.domain.models.query import SimilarTask
from app.domain.services.similar_task_searcher import SimilarTaskSearcher


class EmptySimilarTaskSearcher(SimilarTaskSearcher):
    async def search(self, query_text: str) -> list[SimilarTask]:
        return []
