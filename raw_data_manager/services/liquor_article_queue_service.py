from django.shortcuts import get_object_or_404
from raw_data_manager.forms import SearchLiquorArticleQueueForm
from raw_data_manager.models import RawLiquor, SearchLiquorArticleQueue
from ..repositories.search_liquor_article_queue_repository import SearchLiquorArticleQueueRepository

import logging
logger = logging.getLogger('django')
class SearchLiquorArticleQueueService:
    def __init__(self):
        self.queue_repo = SearchLiquorArticleQueueRepository()

    def get_all_queues(self):
        return self.queue_repo.get_all()

    def get_queue_by_id(self, queue_id):
        return self.queue_repo.get_by_id(queue_id)

    def get_standby_queue(self):
        queue = self.queue_repo.get_standby_queue()
        if queue == None:
            return None
        # 상태 업데이트
        queue.state = 1
        queue.save()
        return queue

    def create_queue(self, data):
        logger.info(f"article create queue// data=> {data}")
        form = SearchLiquorArticleQueueForm(data)
        if form.is_valid():
            liquor_id = form.cleaned_data.get('liquor_id')
            if liquor_id:
                # liquor_id로 RawLiquor 객체 찾기
                liquor_instance = get_object_or_404(RawLiquor, liquor_id=liquor_id)
                queue = form.save(commit=False)
                queue.liquor = liquor_instance
                queue.save()
                
            # 폼을 통해 유효성 검사 후 데이터 저장
            return form.save()  # 새로운 Queue를 생성하고 저장
        else:
            # 유효하지 않은 데이터일 경우 오류 메시지 반환
            logger.info(f"invalidated queue data: {form.errors}")
            return form.errors

    def update_queue(self, queue_id, state, total_collected, new_collected, failed_count, liquor_id=None):
        return self.queue_repo.update(queue_id, state, total_collected, new_collected, failed_count, liquor_id)

    def delete_queue(self, queue_id):
        return self.queue_repo.delete(queue_id)

    def create_by_liquors(self):
        """
        전체 주류 데이터를 조회해서 아티클 검색 큐를 생성
        """
        TARGET_SEARCH_COUNT = 10
        sub_keywords = ["역사", "테이스팅", "리뷰", "후기", "페어링"]

        # 술 조회
        batch_size = 100  # 한 번에 처리할 데이터 수
        #queryset = RawLiquor.objects.all().iterator(chunk_size=batch_size)
        queryset = RawLiquor.objects.all().order_by('-liquor_id')[:20]

        for liquor in queryset:
            for sub_keyword in sub_keywords:
                keyword = f"{liquor.name_kr} {sub_keyword}"
                logger.info(f"{liquor.liquor_id} => {keyword}")
                # 서치 큐 저장
                queue_data = {
                    'keyword': keyword,
                    'target_search_count': TARGET_SEARCH_COUNT,
                    'searched_count': 0,
                    'collected_count': 0,
                    'dup_count': 0,
                    'failed_count': 0,
                    'liquor_id': liquor.liquor_id
                }

                self.create_queue(queue_data)




