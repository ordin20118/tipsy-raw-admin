# repositories.py
from ..models import SearchLiquorArticleQueue, RawLiquor

class SearchLiquorArticleQueueRepository:
    def get_all(self):
        return SearchLiquorArticleQueue.objects.all()

    def get_by_id(self, queue_id):
        return SearchLiquorArticleQueue.objects.get(id=queue_id)

    def create(self, keyword, state, total_collected, new_collected, failed_count, liquor_id=None):
        liquor = RawLiquor.objects.get(id=liquor_id) if liquor_id else None
        return SearchLiquorArticleQueue.objects.create(
            keyword=keyword,
            state=state,
            total_collected=total_collected,
            new_collected=new_collected,
            failed_count=failed_count,
            liquor=liquor
        )

    def update(self, queue_id, state, total_collected, new_collected, failed_count, liquor_id=None):
        queue = self.get_by_id(queue_id)
        liquor = RawLiquor.objects.get(id=liquor_id) if liquor_id else None
        queue.state = state
        queue.total_collected = total_collected
        queue.new_collected = new_collected
        queue.failed_count = failed_count
        queue.liquor = liquor
        queue.save()
        return queue

    def delete(self, queue_id):
        queue = self.get_by_id(queue_id)
        queue.delete()
        return queue
