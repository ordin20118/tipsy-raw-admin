from datetime import timedelta, datetime
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
import mimetypes
import PIL.Image as pilimg
import os
import requests
import json
import logging

logger = logging.getLogger('django')


@api_view(['GET'])
def dashboardCount(request):
    
    if request.method == 'GET':
        target = int(request.GET.get('target', None))
        type = int(request.GET.get('type', None))
        start_date = int(request.GET.get('start_date', None))
        end_date = int(request.GET.get('end_date', None))

        if target == None:
            # return 500
            pass

    else:
        pass


@api_view(['GET'])
def newContentTimeline(request):
    
    if request.method == 'GET':
        
        #now = timezone.now()
        now = datetime.now()
        count_timeline = []

        for i in range(10):            
            h = now - timedelta(hours=i)
            hour_start = h.strftime("%Y-%m-%d %H:00:00")
            hour_end = h.strftime("%Y-%m-%d %H:59:59")

            q = Q()
            q.add(Q(reg_date__range=[hour_start, hour_end]), q.OR)
            q.add(Q(job_code=1001) | Q(job_code=2001) | Q(job_code=3001) | Q(job_code=4001) | Q(job_code=5001), q.AND)

            hour_nac = ManageLog.objects.filter(q)
            hour_nac_count = hour_nac.count()
            obj = {
                'start_date': hour_start,
                'end_date': hour_end,
                'count': hour_nac_count
            }
            count_100 = hour_nac.filter(content_type=100).count()
            count_200 = hour_nac.filter(content_type=200).count()
            count_300 = hour_nac.filter(content_type=300).count()
            count_400 = hour_nac.filter(content_type=400).count()
            count_500 = hour_nac.filter(content_type=500).count()
            obj['count_100'] = count_100
            obj['count_200'] = count_200
            obj['count_300'] = count_300
            obj['count_400'] = count_400
            obj['count_500'] = count_500
            count_timeline.append(obj)

        return HttpResponse(json.dumps({'result': count_timeline}), content_type="application/json")
        #return Response(json.dumps({'result': count_timeline}))

    else:
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def manageTimeline(request):
    
    if request.method == 'GET':
        log_list = ManageLog.objects.order_by('-id').select_related('admin')[:7]
        res = ManageLogSerializer(log_list, many=True)
        return Response(res.data)

    else:
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def crawledDataStats(request):
    
    if request.method == 'GET':
        agg_qset = (
            CrawledLiquor.objects
            .filter(category2__isnull=False)            # where : category2 외래 키가 있는 경우 필터링
            .values('category2_id', 'category2__name')  # select : category2 외래 키와 그의 name 필드를 선택
            .annotate(cnt=Count('category2__name'))     # group by count : category2__name 필드를 기준으로 그룹화하여 개수 세기
            .annotate(name=F('category2__name'))        # set field : 필드 설정
            .annotate(category_id=F('category2_id'))    # set field : 필드 설정
            .values('category_id', 'name', 'cnt')       # select : 필요한 필드들만 선택
        )

        res = []
        for qset in agg_qset:
            res.append(qset)


        return HttpResponse(json.dumps({'result': res}), content_type="application/json")

    else:
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def liquorDataStats(request):
    
    if request.method == 'GET':
        agg_qset = (
            RawLiquor.objects
            .filter(category2_id__isnull=False)         # where 
            .values('category2_id', 'category2__name')  # select
            .annotate(cnt=Count('category2__name'))     # group by count
            .annotate(name=F('category2__name'))        # set field
            .annotate(category_id=F('category2_id'))    # set field
            .values('category_id', 'name', 'cnt')       # select
        )

        res = []
        for qset in agg_qset:
            res.append(qset)


        return HttpResponse(json.dumps({'result': res}), content_type="application/json")

    else:
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)