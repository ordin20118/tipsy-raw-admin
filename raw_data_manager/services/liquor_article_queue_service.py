from django.shortcuts import get_object_or_404
from raw_data_manager.forms import SearchLiquorArticleQueueForm
from raw_data_manager.models import RawLiquor
from ..repositories.search_liquor_article_queue_repository import SearchLiquorArticleQueueRepository

class SearchLiquorArticleQueueService:
    def __init__(self):
        self.queue_repo = SearchLiquorArticleQueueRepository()

    def get_all_queues(self):
        return self.queue_repo.get_all()

    def get_queue_by_id(self, queue_id):
        return self.queue_repo.get_by_id(queue_id)

    def create_queue(self, data):
        form = SearchLiquorArticleQueueForm(data)
        if form.is_valid():
            liquor_id = form.cleaned_data.get('liquor_id')
            if liquor_id:
                # liquor_id로 RawLiquor 객체 찾기
                liquor_instance = get_object_or_404(RawLiquor, id=liquor_id)
                queue = form.save(commit=False)
                queue.liquor = liquor_instance
                queue.save()
                
            # 폼을 통해 유효성 검사 후 데이터 저장
            return form.save()  # 새로운 Queue를 생성하고 저장
        else:
            # 유효하지 않은 데이터일 경우 오류 메시지 반환
            return form.errors

    def update_queue(self, queue_id, state, total_collected, new_collected, failed_count, liquor_id=None):
        return self.queue_repo.update(queue_id, state, total_collected, new_collected, failed_count, liquor_id)

    def delete_queue(self, queue_id):
        return self.queue_repo.delete(queue_id)
