import json
import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from raw_data_manager.services.ai_service import ana_description

logger = logging.getLogger('django')

@api_view(['GET', 'POST'])
def ana_description_with_chatgpt(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        data = json.loads(request.body)
        crawled_liquor_id = int(data.get('crawled_liquor_id'))

        if crawled_liquor_id == None:
            return Response("Bad Request!", status=status.HTTP_400_BAD_REQUEST)

        return Response(ana_description(crawled_liquor_id))
