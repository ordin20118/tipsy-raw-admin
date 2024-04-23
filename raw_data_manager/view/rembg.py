from datetime import timedelta, datetime
from io import BytesIO
from django.utils import timezone
from email.contentmanager import raw_data_manager
from re import L
from django.utils import timezone
from core.settings import DATA_ROOT, IMAGE_PATH, SVC_MGR_URL
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from raw_data_manager.forms import *
from raw_data_manager.models import *
from raw_data_manager.classes import *
from raw_data_manager.serializers import *
from utils.ImageUtil import *
from django.template import loader
from django.http import HttpResponse
from rest_framework import status
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.core import serializers
import PIL.Image as pilimg
import requests
import logging
from rembg import remove
from core.settings import S3_URL

logger = logging.getLogger('django')

@api_view(['GET', 'POST'])
def rembg(request):
    if request.method == 'GET':
        return get_rembg_queue_view(request)
    elif request.method == 'POST':
        return save_rembg_queue(request)

def get_rembg_queue_view(request):
    id = int(request.GET.get('id', None))
    org_image_id = int(request.GET.get('org_image_id', None))

    if id == None and org_image_id == None:
        return Response("Invalid parameters!", status=status.HTTP_400_BAD_REQUEST)

    queue_data = None
    if id != None:
        queue_data = get_queue_by_id(id=id)
    elif org_image_id != None:
        queue_data = get_standby_queue_by_image_id(org_image_id=org_image_id)

    return queue_data
    
# 큐 id를 이용한 조회
def get_queue_by_id(id):
    queue = RembgQueue.objects.get(id=id)
    serialized_queue = RembgQueueSerializer(queue)
    return serialized_queue

# 이미지 id에 대한 큐 중 대기 상태의 큐 조회 
def get_standby_queue_by_image_id(org_image_id):
    queue = RembgQueue.objects.filter(org_image_id=org_image_id, state=RembgQueue.STATE_STANDBY)
    if len(queue) > 0:
        return queue
    else:
        return None

# 대기중인 큐 조회

def get_and_process_queue():
    # 대기중 큐 조회
    queryset = RembgQueue.objects.filter(state=RembgQueue.STATE_STANDBY).order_by('id')[:1]
    
    if queryset.exists():
        # 큐가 있는 경우
        queue = queryset.first()
        queue.state = RembgQueue.STATE_PROCESS
        queue.save(update_fields=['state'])
        
        logger.info("[Process Queue]")
        logger.info(queue)
        process_rembg(queue)
    else:
        # 큐가 없는 경우
        return None

@transaction.atomic
def process_rembg(queue):
    try:
        # 변경 대상 이미지 조회
        logger.info("변경 대상 이미지 ID:%d" % queue.org_image_id)

        target_image = Image.objects.get(image_id=queue.org_image_id)
        
        # 원본 이미지 url을 이용해서 조회
        image_url = S3_URL + '/' + target_image.s3_key
        response = requests.get(image_url)
        if response.status_code == 200:
            # PIL을 사용하여 이미지 열기
            input_image = pilimg.open(BytesIO(response.content))

            # 배경 제거된 이미지
            output_image = remove(input_image)
            # 임시 파일로 저장 - 확장자 설정을 위해서
            output_image.format = target_image.extension

            # 기존 이미지에 대한 처리
            if target_image.image_type == Image.IMG_TYPE_REP:
                # - 원본 이미지가 대표라면 대표에서 일반으로 변경 + 사용 불가 상태로 변경 
                target_image.image_type = Image.IMG_TYPE_NORMAL
                target_image.is_open = Image.IMG_STATUS_PRV
                target_image.save(update_fields=['image_type', 'is_open'])
            else:
                # - 원본 이미지가 대표가 아닌 경우 원본 이미지는 사용 불가 상태로 변경 + 대표 이미지를 일반으로 변경 (상태는 변경x)
                target_image.is_open = Image.IMG_STATUS_PRV
                target_image.save(update_fields=['image_type', 'is_open'])

                rep_image = Image.objects.get(image_type=Image.IMG_TYPE_REP, 
                                                        content_type=target_image.content_type,
                                                        content_id=target_image.content_id)
                rep_image.image_type = Image.IMG_TYPE_NORMAL
                rep_image.save(update_fields=['image_type'])
        
            # s3 저장
            s3_key = saveImgToS3(image_file=output_image, path='image/liquor', ext=target_image.extension)

            # 이미지 정보 db 저장 (대표로 설정)
            rembg_image = Image()
            rembg_image.is_open = Image.IMG_STATUS_PUB
            rembg_image.image_type = Image.IMG_TYPE_REP
            rembg_image.content_type = target_image.content_type
            rembg_image.content_id = target_image.content_id
            rembg_image.s3_key = s3_key
            rembg_image.extension = output_image.format.lower()
            rembg_image.save()

            # 큐 상태 업데이트
            queue.state = RembgQueue.STATE_FINISH
            queue.out_image_id = rembg_image.image_id
            queue.save(update_fields=['state', 'out_image_id', 'update_date'])
            
        else:
            logger.error("배경을 제거할 이미지를 다운로드할 수 없습니다.")
            queue.state = RembgQueue.STATE_FAIL
            queue.save(update_fields=['state', 'update_date'])
    except Image.DoesNotExist:
        logger.info("해당하는 이미지를 찾을 수 없습니다.[%d]" % queue.org_image_id)
    except Exception as e:
        logger.error(e)
        queue.state = RembgQueue.STATE_FAIL
        queue.save(update_fields=['state', 'update_date'])
        raise e


def save_rembg_queue(request):

    form = RembgQueueForm(request.POST)
        
    if form.is_valid():
        rembg_queue = form.save(False)
        rembg_queue.state = RembgQueue.STATE_STANDBY

        prev_queue = RembgQueue.objects.filter(org_image_id=rembg_queue.org_image_id, state=RembgQueue.STATE_STANDBY)

        if len(prev_queue) > 0:
            serialized_queue = RembgQueueSerializer(prev_queue) 
            return Response(serialized_queue.data, status=status.HTTP_200_OK)        

        rembg_queue.save()
    else:
        return Response("Invalid parameters!", status=status.HTTP_400_BAD_REQUEST)

    serialized_queue = RembgQueueSerializer(rembg_queue) 
    return Response(serialized_queue.data, status=status.HTTP_200_OK)



@api_view(['PUT'])
def update_rembg_queue(request):
    
    data = request.data
    form = CrawledLiquorImageForm(request.POST)
        
    if form.is_valid():
        crawled_image = CrawledLiquorImage()
        crawled_image.id = data['id']
        crawled_image.is_use = data['is_use']
        crawled_image.save(update_fields=['is_use'])
    else:
        return Response("Invalid parameters!", status=status.HTTP_400_BAD_REQUEST)

    serialized_image = CrawledLiquorImageSerializer(crawled_image) 
    return Response(serialized_image.data, status=status.HTTP_200_OK)