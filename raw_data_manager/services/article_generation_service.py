from django.db import transaction

from raw_data_manager.services.ai_service import AiService
from ..repositories.article_generation_repository import ArticleGenerationQueueRepository

class ArticleGenerationService:

    def __init__(self, summarizer):
        self.ai_service = AiService()

    def process_batch(self, limit=10):
        with transaction.atomic():
            jobs = ArticleGenerationQueueRepository.get_pending_jobs(limit)

            for job in jobs:
                try:
                    ArticleGenerationQueueRepository.mark_in_progress(job)

                    # 술 본문 만들기 호출
                    self.ai_service.ana_articles(job.liquor.liquor_id)

                    ArticleGenerationQueueRepository.mark_completed(job)

                except Exception as e:
                    ArticleGenerationQueueRepository.mark_failed(job, str(e))
