from django.db import transaction
from django.utils import timezone
from ..models import ArticleGenerationQueue

class ArticleGenerationQueueRepository:

    @staticmethod
    def get_pending_jobs(limit=10):
        return (
            ArticleGenerationQueue.objects
            .select_for_update(skip_locked=True)
            .filter(status='pending')
            .order_by('created_at')[:limit]
        )

    @staticmethod
    def mark_in_progress(job):
        job.status = 'in_progress'
        job.started_at = timezone.now()
        job.save()

    @staticmethod
    def mark_completed(job):
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()

    @staticmethod
    def mark_failed(job, error_message):
        job.status = 'failed'
        job.error_message = error_message
        job.retries += 1
        job.save()

    @staticmethod
    def create_job(alcohol_id):
        return ArticleGenerationQueue.objects.create(
            alcohol_id=alcohol_id,
            status='pending'
        )
