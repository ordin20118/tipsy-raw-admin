from email.contentmanager import raw_data_manager
from tkinter import image_types
from django.utils import timezone
from core.settings import DATA_ROOT, IMAGE_PATH
from rest_framework.response import Response
from rest_framework.decorators import api_view
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
import mimetypes
import PIL.Image as pilimg
import string
import random
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
        return None


def makeCategTree(parentId, treeKey, childDic, treeList):
    
    if len(treeKey) == 0:
        treeKey += str(parentId)
    else:
        treeKey += "^" + str(parentId)

    hasChild = False
    if parentId in childDic:
        hasChild = True
        
        tree = makeTreeInstance(treeKey)
        treeList.append(tree)
        # 또 자식 확인
        childs = childDic[parentId]
        for child in childs:
            makeCategTree(child.id, treeKey, childDic, treeList)
    else:
        tree = makeTreeInstance(treeKey)
        treeList.append(tree)

# make CategoryTree instance from category tree key
def makeTreeInstance(treeKey):
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
def categTree(request):
    
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
                makeCategTree(categ.id, '', categChilds, categTrees)


        serializedTree = CategoryTreeSerializer(categTrees, many=True)

        # Update Data Example
        for tree in categTrees:
            tree.save()
        
        return Response(serializedTree.data)
        #return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def liquor(request):
    
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
                liquor.reg_date = timezone.now()
                liquor.save()

                liquorStr = RawLiquorSerializer(liquor) 
                
                liquorId = liquor.liquor_id
                print("[pk 확인] => %s" % liquorId)


                # save img data
                imageFile = request.FILES.get('image_file', False)

                if imageFile == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    imgData = Image()
                    imgData.image_type = Image.IMG_TYPE_REP
                    imgData.content_id = liquorId
                    imgData.content_type = ContentInfo.CONTENT_TYPE_LOQUOR
                    imgData.is_open = Image.IMG_STATUS_PUB
                    imgData.save()


                    print("[이미지 ID 확인 => %s" % imgData.image_id)
                    
                    # 2. 이미지 ID를 이용한 경로 생성
                    imgPath = imageIdToPath(imgData.image_id)

                    print("[생성된 이미지 경로] => %s" % imgPath)

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
        #return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
       