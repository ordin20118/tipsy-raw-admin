from raw_data_manager.forms import SearchLiquorArticleQueueForm
from raw_data_manager.services.liquor_article_queue_service import SearchLiquorArticleQueueService
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_queues(request):
    # GET 요청 시 큐 정보 가져오기
    queue_service = SearchLiquorArticleQueueService()
    queues = queue_service.get_all_queues()
    queues_data = [{'id': queue.id, 'keyword': queue.keyword, 'state': queue.get_state_display()} for queue in queues]
    return Response({'queues': queues_data})

@api_view(['POST'])
def create_queue(request):
    # POST 요청 시 폼을 통해 데이터 받기
    form = SearchLiquorArticleQueueForm(request.data)
    if form.is_valid():
        # 폼이 유효하면 서비스로 넘겨서 처리
        queue_service = SearchLiquorArticleQueueService()
        new_queue = queue_service.create_queue(form.cleaned_data)
        return Response({'id': new_queue.id, 'keyword': new_queue.keyword, 'state': new_queue.get_state_display()})
    else:
        # 폼이 유효하지 않으면 오류 메시지 반환
        return Response({'errors': form.errors}, status=400)

@api_view(['POST'])
def create_queue_by_liquors(request):
    queue_service = SearchLiquorArticleQueueService()
    queue_service.create_by_liquors()
    return Response({'state': 'success'})

