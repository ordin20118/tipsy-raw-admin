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

        print(now)

        count_timeline = []

        for i in range(10):            
            h = now - timedelta(hours=i)
            hour_start = h.strftime("%Y-%m-%d %H:00:00")
            hour_end = h.strftime("%Y-%m-%d %H:59:59")
            hour_nac = ManageLog.objects.filter(reg_date__range=[hour_start, hour_end])
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