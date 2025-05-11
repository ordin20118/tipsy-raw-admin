import json
import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from raw_data_manager.services.ai_service import AiService

logger = logging.getLogger('django')

@api_view(['GET', 'POST'])
def ana_description_with_chatgpt(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        ai_service = AiService()
        data = json.loads(request.body)
        crawled_liquor_id = int(data.get('crawled_liquor_id'))

        if crawled_liquor_id == None:
            return Response("Bad Request!", status=status.HTTP_400_BAD_REQUEST)

        return Response(ai_service.ana_description(crawled_liquor_id))

@api_view(['POST'])
def ana_liquor_articles(request):
    if request.method == 'POST':
        ai_service = AiService()
        data = json.loads(request.body)
        liquor_id = int(data.get('liquor_id'))

        if liquor_id == None:
            return Response("Bad Request!", status=status.HTTP_400_BAD_REQUEST)

        return Response(ai_service.ana_articles(liquor_id=liquor_id))
