from email.contentmanager import raw_data_manager
from django.utils import timezone
from core.settings import DATA_ROOT, IMAGE_PATH
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core import serializers as cserializers
from django.db.models import Count
from django.shortcuts import render
from raw_data_manager.forms import *
from raw_data_manager.models import *
from raw_data_manager.classes import *
from raw_data_manager.serializers import *
from utils.ImagePathUtil import *
from django.template import loader
from django.http import HttpResponse
from rest_framework import status
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
import pickle
import mimetypes
import PIL.Image as pilimg
import string
import random
import json
import os

from utils.ImagePathUtil import imageIdToPath

@api_view(['GET', 'POST'])
def image(request):

    if request.method == 'GET':
        
        #print("This is request URL: %s" % request.path_info)
        pathStr = request.path_info

        # /raw_data_manager/image/ 까지 제거
        pathStr = pathStr.replace('/raw_data_manager/image/', '')

        filename = pathStr.split('/')[-1]
        fl_path = DATA_ROOT + IMAGE_PATH + '/{}'.format(pathStr)
        fl = open(fl_path, 'rb')

        mime_type, _ = mimetypes.guess_type(fl_path)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

    elif request.method == 'POST':
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)


def make_categ_tree(parentId, treeKey, childDic, treeList):
    
    if len(treeKey) == 0:
        treeKey += str(parentId)
    else:
        treeKey += "^" + str(parentId)

    hasChild = False
    if parentId in childDic:
        hasChild = True
        
        tree = make_tree_instance(treeKey)
        treeList.append(tree)
        # 또 자식 확인
        childs = childDic[parentId]
        for child in childs:
            make_categ_tree(child.id, treeKey, childDic, treeList)
    else:
        tree = make_tree_instance(treeKey)
        treeList.append(tree)

# make CategoryTree instance from category tree key
def make_tree_instance(treeKey):
    tree = CategoryTree()
    tree.categ_tree_key = treeKey
    
    keys = treeKey.split('^')
    if len(keys) >= 1:
        tree.category1_id = keys[0]
    if len(keys) >= 2:
        tree.category2_id = keys[1]
    if len(keys) >= 3:
        tree.category3_id = keys[2]
    if len(keys) >= 4:
        tree.category4_id = keys[3]

    tree.reg_date = timezone.now()

    return tree

# 카테고리 트리 만들기
@api_view(['GET', 'POST'])
def categ_tree(request):
    
    if request.method == 'GET':
        # categTrees = CategoryTree.objects.all()	
        # serializer = CategoryTreeSerializer(categTrees, many=True) 
        # print(serializer.data)

        categTrees = CategoryTreeWithName.objects.raw('''
            SELECT 
                tree.*,
                categ1.name as category1_name,
                categ2.name as category2_name,
                categ3.name as category3_name,
                categ4.name as category4_name
            FROM tipsy_raw.category_tree tree
            LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON tree.category1_id = categ1.id
            LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON tree.category2_id = categ2.id
            LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON tree.category3_id = categ3.id
            LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON tree.category4_id = categ4.id
        ''')
        serializer = CategoryTreeWithNameSerializer(categTrees, many=True) 
        return Response(serializer.data)

    elif request.method == 'POST':
        
        categTrees = []
        totalCategs = RawCategory.objects.all()
    
        # make categ child dictionary
        categChilds = {}
        for categ in totalCategs:
            if categ.parent != -1:
                if categ.parent in categChilds:
                    categChilds[categ.parent].append(categ)
                else:
                    categChilds[categ.parent] = []
                    categChilds[categ.parent].append(categ)


        # 자식 확인 - 존재하면 해당 카테고리는 끝단x
        # 자식 반복
        # 자식의 자식 확인
        for categ in totalCategs:
            if categ.parent == -1:
                make_categ_tree(categ.id, '', categChilds, categTrees)


        serializedTree = CategoryTreeSerializer(categTrees, many=True)

        # Update Data Example
        for tree in categTrees:
            tree.save()
        
        return Response(serializedTree.data)


@api_view(['GET'])
def page_info(request, name):

    if request.method == 'GET':

        page = int(request.GET.get('page', 1))
        perPage = int(request.GET.get('perPage', 10))
        totalCount = None

        # 이름에 따라서 테이블 데이터에 대한 페이지 정보 제공
        if name == "liquor":
            totalCount = RawLiquor.objects.all().count()
            pageInfo = Paging(page,totalCount,perPage)
            pages = pageInfo.getPages()
            firstRow = pageInfo.getFirstRow()
            return Response(pageInfo.__dict__)
        elif name == "country":
            return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)

    else:
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def liquor(request):
    
    if request.method == 'GET':

        page = int(request.GET.get('page', 1))
        perPage = int(request.GET.get('perPage', 10))
        totalCount = RawLiquor.objects.all().count()

        pageInfo = Paging(page,totalCount,perPage)
        pages = pageInfo.getPages()
        firstRow = pageInfo.getFirstRow()

        # #liquorList = RawLiquor.objects.order_by('-liquor_id')[firstRow:firstRow+perPage].values()
        # liquorList = list(RawLiquor.objects.order_by('-liquor_id')[firstRow:firstRow+perPage].values())
        # serializer = RawLiquorSerializer(liquorList, many=True) 

    
        # TODO: join에 대한 내용을 model에 반영해서 조회하기
        liquorList = JoinedLiquor.objects.raw('''
            SELECT 
                raw_liquor.*,
                categ1.name as category1_name,
                categ2.name as category2_name,
                categ3.name as category3_name,
                categ4.name as category4_name,
                country.name as country_name,
                reg_user.username as reg_admin_name,
                update_user.username as update_admin_name
            FROM tipsy_raw.raw_liquor
            LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = raw_liquor.category1_id
            LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = raw_liquor.category2_id
            LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = raw_liquor.category3_id
            LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = raw_liquor.category4_id
            LEFT OUTER JOIN tipsy_raw.country ON country.country_id = raw_liquor.country_id
            LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = raw_liquor.reg_admin
            LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = raw_liquor.update_admin
        ''')
        
        serializer = JoinedLiquorSerializer(liquorList, many=True) 
     

        # TODO: 이미지는 모두 조회해서 대표가 있는 경우 대표 이미지를 주고
        # 대표 이미지가 없다면 뭘 주나..?
        # 이미지 리스트를 model에 추가해서 줄 수 있나...?

    

        # TODO: 페이징 정보와 함께 묶어서 Serialize 해주고싶지만 하지못함
        #sParam = SearchParam()
        #sParam.list = liquorList
        #res = cserializers.serialize("json", paramList)
        #res = json.dumps(sParam, cls=DjangoJSONEncoder)
        #res = json.dumps(sParam.paging.__dict__, default=str)
        

        
        return Response(serializer.data)
        

    elif request.method == 'POST':
        respone = 'this is test response'
        
        print(request.POST)
        print("\n\n")

        # 술 데이터 저장 + 이미지 저장 트랜잭션 처리
        with transaction.atomic():

            # validate data
            form = LiquorForm(request.POST, request.FILES)
            
            if form.is_valid():
                print("Valid!!")
                # save liquor data in DB
                liquor = form.save(commit=False)
                liquor.upload_state = 0
                liquor.update_state = 0
                liquor.reg_admin = request.user.id
                liquor.reg_date = timezone.now()
                liquor.save()

                liquorId = liquor.liquor_id

                    # admin_id = models.IntegerField()
                    # job_code = models.IntegerField(blank=True, null=True)
                    # job_name = models.CharField(max_length=45, blank=True, null=True)
                    # content_id = models.IntegerField(blank=True, null=True)
                    # content_type = models.IntegerField(blank=True, null=True)
                    # reg_date = models.DateTimeField(auto_now_add=True)
                logInfo = ManageLog()
                logInfo.admin_id = request.user.id
                logInfo.job_code = JobInfo.JOB_ADD_SPIRITS
                logInfo.job_name = JobInfo.JOBN_ADD_SPIRITS
                logInfo.content_id = liquorId
                logInfo.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
                logInfo.save()
                
                # save img data
                imageFile = request.FILES.get('image_file', False)

                if imageFile == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    imgData = Image()
                    imgData.image_type = Image.IMG_TYPE_REP
                    imgData.content_id = liquorId
                    imgData.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
                    imgData.is_open = Image.IMG_STATUS_PUB
                    imgData.save()

                    # 2. 이미지 ID를 이용한 경로 생성
                    imgPath = imageIdToPath(imgData.image_id)

                    # 3. 원본, 300, 600 3가지로 저장          
                    # - 파일 형식: image/{이미지 경로}/{이미지_ID}_{이미지_SIZE}.png
                    # 업로드할 이미지 데이터 pillow로 객체화
                    img = pilimg.open(imageFile)

                    # 저장할 경로 폴더 존재 확인
                    imgDir = DATA_ROOT + IMAGE_PATH + "/" + imgPath + "/"

                    if os.path.isdir(imgDir) == False:
                        os.makedirs(imgDir)
                    
                    imgOrgPath = imgDir + str(imgData.image_id) + '.' + 'png'
                    
                    img.save(imgOrgPath)

                    # resize 300
                    img300Path = imgDir + str(imgData.image_id) + '_300.' + 'png'
                    height_300 = getScaledHeight(img.width, img.height, 300)

                    img300 = img.resize((300, height_300))
                    img300.save(img300Path)

                    # resize 600
                    img600Path = imgDir + str(imgData.image_id) + '_600.' + 'png'
                    height_600 = getScaledHeight(img.width, img.height, 600)
                    
                    img600 = img.resize((600, height_600))
                    img600.save(img600Path)

                    # DB에 이미지 경로 업데이트
                    imgData.path = imgPath + "/" + str(imgData.image_id)
                    imgData.save(update_fields=['path'])

                    # 임시 파일 저장 이름
                    #length_of_string = 8
                    #tmpName = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))

                return Response(respone, status=status.HTTP_200_OK)
            else:
                print("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
        return Response(respone)



# 국가 데이터 API
@api_view(['GET'])
def country(request):
    
    if request.method == 'GET':
        allCountry = Country.objects.all()	
        serializer = CountrySerializer(allCountry, many=True) 
        
        # categTrees = CategoryTreeWithName.objects.raw('''
        #     SELECT 
        #         tree.*,
        #         categ1.name as category1_name,
        #         categ2.name as category2_name,
        #         categ3.name as category3_name,
        #         categ4.name as category4_name
        #     FROM tipsy_raw.category_tree tree
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON tree.category1_id = categ1.id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON tree.category2_id = categ2.id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON tree.category3_id = categ3.id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON tree.category4_id = categ4.id
        # ''')
        # serializer = CategoryTreeWithNameSerializer(categTrees, many=True) 
        return Response(serializer.data)

    elif request.method == 'POST':
       pass 
       