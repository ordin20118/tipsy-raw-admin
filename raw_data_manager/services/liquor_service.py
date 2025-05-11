from django.db import transaction
from raw_data_manager.forms import LiquorContentForm
import logging

from raw_data_manager.repositories.liquor_content_repository import LiquorContentRepository

logger = logging.getLogger('django')

class LiquorService:
    def __init__(self):
        self.liquor_content_repo = LiquorContentRepository()

    def save_liquor_contents(self, liquor_id, data):
        """
        liquor: Liquor 인스턴스
        data: JSON 형식의 본문 데이터
        """
        contents = data.get('contents', [])

        with transaction.atomic():  # 전체 저장이 원자적으로 처리되도록
            # TODO: liquor_id에 대한 contents 모두 제거
            self.liquor_content_repo.delete_by_liquor_id(liquor_id=liquor_id)
            for item in contents:
                form = LiquorContentForm(data={
                    'liquor': liquor_id,
                    'seq': item.get('seq'),
                    'title': item.get('title'),
                    'sub_title': item.get('sub_title'),
                    'content': item.get('content'),
                    'type': item.get('type', 'other'),  # 기본값 지정
                })

                if form.is_valid():
                    form.save()
                else:
                    logger.info("❌ 유효하지 않은 데이터:", form.errors)