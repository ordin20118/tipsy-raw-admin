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
def search(request):
    if request.method == 'GET':

        search_url = SVC_MGR_URL + "/api/search.tipsy?t=tipsy"

        keyword = request.GET.get('keyword')
        if keyword != None:
            search_url += '&keyword=%s'%keyword
        
        target = request.GET.get('target')
        if target != None:
            search_url += '&target=%s'%target

        categId = request.GET.get('categId')
        if categId != None:
            search_url += '&categId=%s'%categId       

        categLv = request.GET.get('categLv')
        if categLv != None:
            search_url += '&categLv=%s'%categLv

        nowPage = request.GET.get('nowPage')
        if nowPage != None:
            search_url += '&nowPage=%s'%nowPage

        pergPage = request.GET.get('pergPage')
        if pergPage != None:
            search_url += '&pergPage=%s'%pergPage


        try:
            search_request = requests.get(search_url)
            #print("\n[text]:%s"%search_request.text)
            #print("\n[status]:%s"%search_request.status_code)
            #print("\n[url]:%s"%search_request.url)
            if search_request.status_code == 200:
                return Response(search_request.text)
            else:
                return Response("ERROR!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response("ERROR!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    elif request.method == 'POST':
        return Response("NOT FOUND", status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def image(request):

    if request.method == 'GET':
        
        #print("This is request URL: %s" % request.path_info)
        pathStr = request.path_info

        # /raw_data_manager/image/ 까지 제거
        pathStr = pathStr.replace('/admin/raw_data_manager/image/', '')

        filename = pathStr.split('/')[-1]
        fl_path = DATA_ROOT + IMAGE_PATH + '/{}'.format(pathStr)
        fl = open(fl_path, 'rb')

        mime_type, _ = mimetypes.guess_type(fl_path)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

    elif request.method == 'POST':
        
        image_form = ImageForm(request.POST, request.FILES)        

        if image_form.is_valid():
            image = image_form.save(False)
            imageFile = request.FILES.get('image_file', False)

            if imageFile == False:
                raise Exception("No Image File")
            else:

                print("[image type]:%s" % image.image_type)
                print("[image content type]:%s" % image.content_id)
                print("[image content id]:%s" % image.content_type)

                try:
                    with transaction.atomic():

                        if image.image_type == Image.IMG_TYPE_REP:
                            # 기존에 존재하는 이미지중에 대표 이미지 조회 후 수정
                            rep_img = Image.objects.get(image_type=Image.IMG_TYPE_REP, 
                                                        content_type=image.content_type,
                                                        content_id=image.content_id)
                            rep_img.image_type = Image.IMG_TYPE_NORMAL
                            rep_img.save(update_fields=['image_type'])

                            # save image to DB
                            image.save()

                            # save image file
                            img_path = imageIdToPath(image.image_id)
                            saveImgToPath(imageFile, image.image_id, DATA_ROOT+ IMAGE_PATH + "/" + img_path + "/")
            
                            # update image's path to DB
                            image.path = img_path + "/" + str(image.image_id)
                            image.save(update_fields=['path'])

                except Image.DoesNotExist as e:
                    print("There is no rep_img.")   # change to log...
                except Image.MultipleObjectsReturned as e:
                    print("There is multiple rep_img. content_id:%s, content_type:%s" % (image.content_id, image.content_type)) # change to log...
        else:
            return Response("No Validated Request", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PUT':

        # 트랜잭션
        # 대표로 지정된 경우 해당 컨텐츠의 다른 이미지를 불러와서
        # 일반 이미지로 변경한다.

        # 수정 완료


        return Response("This is image PUT return")

    elif request.method == 'DELETE':
        req_data = ImageForm(request.POST)

        #print(request.POST.get("is_delete"))
        
        if req_data.is_valid():

            print("%d 이미지 제거" % req_data.cleaned_data['image_id'])

            # 트랜잭션
            with transaction.atomic():

                image_id = req_data.cleaned_data['image_id']

                if image_id is None and image_id <= 0:
                    return Response("No Validated Image ID", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # DB 데이터 제거
                img_data = Image.objects.get(pk=image_id)
                img_data.delete()

                # 이미지 파일 제거
                imgPath = imageIdToPath(image_id)
                imgDir = DATA_ROOT + IMAGE_PATH + "/" + imgPath + "/"
                os.remove(imgDir + str(image_id) + '.' + 'png')
                os.remove(imgDir + str(image_id) + '_300.' + 'png')
                os.remove(imgDir + str(image_id) + '_600.' + 'png')

        return Response("This is image DELETE return")


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
                categ4.name as category4_name,
                categ1.name_en as category1_name_en,
                categ2.name_en as category2_name_en,
                categ3.name_en as category3_name_en,
                categ4.name_en as category4_name_en
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


@api_view(['GET', 'POST', 'PUT'])
def liquor(request):

    logger.info("[liquor API]");
    logger.info(request.method);
    
    if request.method == 'GET':

        page = int(request.GET.get('page', 1))
        perPage = int(request.GET.get('perPage', 10))
        totalCount = RawLiquor.objects.all().count()    # TODO: 비효율적인 코드

        pageInfo = Paging(page,totalCount,perPage)
        pages = pageInfo.getPages()
        firstRow = pageInfo.getFirstRow()

        # #liquorList = RawLiquor.objects.order_by('-liquor_id')[firstRow:firstRow+perPage].values()
        # liquorList = list(RawLiquor.objects.order_by('-liquor_id')[firstRow:firstRow+perPage].values())
        # serializer = RawLiquorSerializer(liquorList, many=True) 

    
        # TODO: join에 대한 내용을 model에 반영해서 조회하기
        liquorList = JoinedLiquor.objects.order_by('-liquor_id').raw('''
            SELECT 
                raw_liquor.*,
                categ1.name as category1_name,
                categ2.name as category2_name,
                categ3.name as category3_name,
                categ4.name as category4_name,
                country.name as country_name,
                reg_user.username as reg_admin_name,
                update_user.username as update_admin_name,
                if(image.path is null, 'default', image.path) as rep_img
            FROM tipsy_raw.raw_liquor
            LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = raw_liquor.category1_id
            LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = raw_liquor.category2_id
            LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = raw_liquor.category3_id
            LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = raw_liquor.category4_id
            LEFT OUTER JOIN tipsy_raw.country ON country.country_id = raw_liquor.country_id
            LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = raw_liquor.reg_admin
            LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = raw_liquor.update_admin
            LEFT OUTER JOIN image ON image.content_id = raw_liquor.liquor_id AND image.content_type = 100 AND image.image_type = 0
        ''')


        paginator = Paginator(liquorList, perPage)  # 페이지당 10개씩 보여주기
        page_obj = paginator.get_page(page)

        serializer = JoinedLiquorSerializer(page_obj, many=True) 
        #serializer = JoinedLiquorSerializer(liquorList, many=True) 
     
        # TODO: 페이징 정보와 함께 묶어서 Serialize 해주고싶지만 하지못함
        #sParam = SearchParam()
        #sParam.list = liquorList
        #res = cserializers.serialize("json", paramList)
        #res = json.dumps(sParam, cls=DjangoJSONEncoder)
        #res = json.dumps(sParam.paging.__dict__, default=str)
        
        return Response(serializer.data)
        

    elif request.method == 'POST':
        respone = 'Success Save Liquor Data'

        # 술 데이터 저장 + 이미지 저장 트랜잭션 처리
        with transaction.atomic():

            # validate data
            form = LiquorForm(request.POST, request.FILES)
            
            if form.is_valid():
                # save liquor data in DB
                liquor = form.save(commit=False)
                liquor.upload_state = RawLiquor.UPLOAD_STATE_NOT_YET
                liquor.update_state = RawLiquor.UPDATE_STATE_NORMAL
                liquor.site = 0
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
                    img_path = imageIdToPath(imgData.image_id)
                    saveImgToPath(imageFile, imgData.image_id, DATA_ROOT+ IMAGE_PATH + "/" + img_path + "/")

                    # DB에 이미지 경로 업데이트
                    imgData.path = img_path + "/" + str(imgData.image_id)
                    imgData.save(update_fields=['path'])

                    # 임시 파일 저장 이름
                    #length_of_string = 8
                    #tmpName = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))

                return Response(respone, status=status.HTTP_200_OK)
            else:
                print("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'PUT':

        logger.info(request.POST)

        form = LiquorForm(request.POST)
        
        if form.is_valid():
            liquor = form.save(commit=False)            
            
            liquor_id = liquor.liquor_id

            print("updated liquor id: %s"% id)

            # 변경 내용 확인
            prev_liquor = RawLiquor.objects.get(liquor_id=liquor_id)

            prev_info = {}
            updated_info = {}

            # name_kr
            if prev_liquor.name_kr != liquor.name_kr:
                prev_info['name_kr'] = prev_liquor.name_kr
                updated_info['name_kr'] = liquor.name_kr
                prev_liquor.name_kr = liquor.name_kr
            
            # name_en
            if prev_liquor.name_en != liquor.name_en:
                prev_info['name_en'] = prev_liquor.name_en
                updated_info['name_en'] = liquor.name_en
                prev_liquor.name_en = liquor.name_en
            
            # # upload_state
            # if prev_liquor.upload_state != liquor.upload_state:
            #     prev_info['upload_state'] = prev_liquor.upload_state
            #     updated_info['upload_state'] = liquor.upload_state
            #     prev_liquor.upload_state = liquor.upload_state

            # # update_state
            # if prev_liquor.update_state != liquor.update_state:
            #     prev_info['update_state'] = prev_liquor.update_state
            #     updated_info['update_state'] = liquor.update_state
            #     prev_liquor.update_state = liquor.update_state

            # vintage
            if prev_liquor.vintage != liquor.vintage:
                prev_info['vintage'] = prev_liquor.vintage
                updated_info['vintage'] = liquor.vintage
                prev_liquor.vintage = liquor.vintage

            # abv
            if prev_liquor.abv != liquor.abv:
                prev_info['abv'] = prev_liquor.abv
                updated_info['abv'] = liquor.abv
                prev_liquor.abv = liquor.abv

            # country_id
            if prev_liquor.country_id != liquor.country_id:
                prev_info['country_id'] = prev_liquor.country_id
                updated_info['country_id'] = liquor.country_id
                prev_liquor.country_id = liquor.country_id

            # region
            if prev_liquor.region != liquor.region:
                prev_info['region'] = prev_liquor.region
                updated_info['region'] = liquor.region
                prev_liquor.region = liquor.region

            # region_id
            if prev_liquor.region_id != liquor.region_id:
                prev_info['region_id'] = prev_liquor.region_id
                updated_info['region_id'] = liquor.region_id
                prev_liquor.region_id = liquor.region_id

            # category1_id
            if prev_liquor.category1_id != liquor.category1_id:
                prev_info['category1_id'] = prev_liquor.category1_id
                updated_info['category1_id'] = liquor.category1_id
                prev_liquor.category1_id = liquor.category1_id

            # category2_id
            if prev_liquor.category2_id != liquor.category2_id:
                prev_info['category2_id'] = prev_liquor.category2_id
                updated_info['category2_id'] = liquor.category2_id
                prev_liquor.category2_id = liquor.category2_id

            # category3_id
            if prev_liquor.category3_id != liquor.category3_id:
                prev_info['category3_id'] = prev_liquor.category3_id
                updated_info['category3_id'] = liquor.category3_id
                prev_liquor.category3_id = liquor.category3_id

            # category4_id
            if prev_liquor.category4_id != liquor.category4_id:
                prev_info['category4_id'] = prev_liquor.category4_id
                updated_info['category4_id'] = liquor.category4_id
                prev_liquor.category4_id = liquor.category4_id

            # description
            if prev_liquor.description != liquor.description:
                prev_info['description'] = prev_liquor.description
                updated_info['description'] = liquor.description
                prev_liquor.description = liquor.description

            # history
            if prev_liquor.history != liquor.history:
                prev_info['history'] = prev_liquor.history
                updated_info['history'] = liquor.history
                prev_liquor.history = liquor.history

            prev_liquor.update_state = ContentInfo.UPDATE_STATE_NEED_CONFIRM
            prev_liquor.update_admin = request.user.id
            prev_liquor.update_date = timezone.now()
            #liquor.save()
            prev_liquor.save(update_fields=['name_kr', 'name_en', 'vintage', 'abv', 'country_id', 'description', 'region',
                                        'upload_state', 'update_state', 'price', 'history', 'update_admin', 'region_id',
                                        'update_date', 'category1_id', 'category2_id', 'category3_id', 'category4_id'])

            info = {
                "prev_info": prev_info,
                "updated_info": updated_info
            }
            info_str = json.dumps(info, ensure_ascii=False)

            logInfo = ManageLog()
            logInfo.admin_id = request.user.id
            logInfo.job_code = JobInfo.JOB_MODIFY_SPIRITS
            logInfo.job_name = JobInfo.JOBN_MODIFY_SPIRITS
            logInfo.content_id = liquor_id
            logInfo.info = info_str
            logInfo.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
            logInfo.save()
            return Response("success", status=status.HTTP_200_OK)
        else:
            print("No Validated")
            # TODO: return error response
            return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def cocktail(request):
    
    if request.method == 'GET':

        page = int(request.GET.get('page', 1))
        perPage = int(request.GET.get('perPage', 10))        
    
        # TODO: join에 대한 내용을 model에 반영해서 조회하기
        cocktailList = JoinedCocktail.objects.order_by('-cocktail_id').raw('''
            SELECT 
                raw_liquor.*,
                31 as category1_name,
                null as category2_name,
                null as category3_name,
                null as category4_name,
                reg_user.username as reg_admin_name,
                update_user.username as update_admin_name,
                if(image.path is null, 'default', image.path) as rep_img
            FROM tipsy_raw.cocktail
            LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = cocktail.reg_admin
            LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = cocktail.update_admin
            LEFT OUTER JOIN image ON image.content_id = cocktail.cocktail_id AND image.content_type = 200 AND image.image_type = 0
        ''')


        paginator = Paginator(cocktailList, perPage)  # 페이지당 10개씩 보여주기
        page_obj = paginator.get_page(page)

        serializer = JoinedCocktailSerializer(page_obj, many=True)       
        
        return Response(serializer.data)
        

    elif request.method == 'POST':
        respone = 'Success Save Cocktail Data'

        # 칵테일 데이터 저장 + 이미지 저장 트랜잭션 처리
        with transaction.atomic():

            # validate data
            form = CocktailForm(request.POST, request.FILES)
            
            if form.is_valid():
                # save cocktail data in DB
                cocktail = form.save(commit=False)
                cocktail.upload_state = 0
                cocktail.update_state = 0
                cocktail.reg_admin = request.user.id
                cocktail.reg_date = timezone.now()
                cocktail.save()

                cocktailId = cocktail.cocktail_id

                logInfo = ManageLog()
                logInfo.admin_id = request.user.id
                logInfo.job_code = JobInfo.JOB_ADD_COCKTAIL
                logInfo.job_name = JobInfo.JOBN_ADD_COCKTAIL
                logInfo.content_id = cocktailId
                logInfo.content_type = ContentInfo.CONTENT_TYPE_COCTAIL
                logInfo.save()
                
                # save img data
                imageFile = request.FILES.get('image_file', False)

                if imageFile == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    imgData = Image()
                    imgData.image_type = Image.IMG_TYPE_REP
                    imgData.content_id = cocktailId
                    imgData.content_type = ContentInfo.CONTENT_TYPE_COCTAIL
                    imgData.is_open = Image.IMG_STATUS_PUB
                    imgData.save()

                    # 2. 이미지 ID를 이용한 경로 생성
                    img_path = imageIdToPath(imgData.image_id)
                    saveImgToPath(imageFile, imgData.image_id, DATA_ROOT+ IMAGE_PATH + "/" + img_path + "/")

                    # DB에 이미지 경로 업데이트
                    imgData.path = img_path + "/" + str(imgData.image_id)
                    imgData.save(update_fields=['path'])

                    # 임시 파일 저장 이름
                    #length_of_string = 8
                    #tmpName = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))

                return Response(respone, status=status.HTTP_200_OK)
            else:
                logger.info("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'PUT':

        # 정보 데이터 수정 
        # ★★★ 1. 수정된 정보만 받는다.
        # 2. 기존 데이터 가져와서 수정된 정보로 수정한다.
        # 3. 로그에는 이전 정보와 수정된 내용을 JSON 형태로 저장한다.
        
        # 비활성화
        pass

    elif request.method == 'DELETE':

        logger.info("[[Enter Cocktail Remove]]")

        form = CocktailDelForm(request.POST)
    
        if form.is_valid():

            logger.info("[[It's Valid!]]")

            cocktail_form = form.get_obj()            
            cocktail_id = cocktail_form.cocktail_id

            # 칵테일 데이터 조회
            cocktail = Cocktail.objects.get(cocktail_id=cocktail_id)

            logInfo = ManageLog()
            logInfo.admin_id = request.user.id
            logInfo.job_code = JobInfo.JOB_REMOVE_COCKTAIL
            logInfo.job_name = JobInfo.JOBN_REMOVE_COCKTAIL
            logInfo.content_id = cocktail_id
            logInfo.content_type = ContentInfo.CONTENT_TYPE_COCTAIL

            # 데이터가 없는 경우 에러 반환 - No Validated Data
            try:
                with transaction.atomic():

                    # 이미지 제거
                    # - 파일이 존재하지 않는 경우 칵테일 상태 에러로 변경 후 관리 로그에 에러 메시지 남기기
                    # 이미지 DB 데이터 제거
                    #   - 컨텐츠 타입과 ID를 통해서 모든 이미지 조회 후 객체.delete() 하면 된다.
                    image_set = Image.objects.filter(content_type=ContentInfo.CONTENT_TYPE_COCTAIL, content_id=cocktail_id)

                    for image in image_set:
                        print(image.path)
                        # 이미지 파일 제거
                        # 이미지 데이터 제거
                        imgPath = imageIdToPath(image.image_id)
                        imgDir = DATA_ROOT + IMAGE_PATH + "/" + imgPath + "/"
                        os.remove(imgDir + str(image.image_id) + '.' + 'png')
                        os.remove(imgDir + str(image.image_id) + '_300.' + 'png')
                        os.remove(imgDir + str(image.image_id) + '_600.' + 'png')
                        image.delete()
                   

                    # 칵테일 DB 데이터 제거
                    cocktail_name = cocktail.name_kr
                    cocktail.delete()
                    
                    # 영구제거 로그 남기기 - 칵테일 아이디와 이름을 남긴다.
                    info_json = {
                        "id": cocktail_id,
                        "name": cocktail_name
                    }

                    logInfo.info = json.dumps(info_json, ensure_ascii=False)
                    logInfo.save()
                    return Response("success", status=status.HTTP_200_OK)               

            except FileNotFoundError as fe:
                cocktail.update_state = ContentInfo.UPDATE_STATE_ERROR
                cocktail.save(update_fields=['update_state'])
                logInfo.info = fe
                logInfo.save()
            except Exception as ex:
                cocktail.update_state = ContentInfo.UPDATE_STATE_ERROR
                cocktail.save(update_fields=['update_state'])
                logInfo.info = ex
                logInfo.save()
            
        else:
            print("No Validated")   # TODO: change to log
            return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET', 'POST'])
def ingredient(request):
    
    if request.method == 'GET':
        return ""        

    elif request.method == 'POST':
        
        respone = 'Success Save Ingredient Data'

        # 재료 데이터 저장 + 이미지 저장 트랜잭션 처리
        with transaction.atomic():

            # validate data
            form = IngredientForm(request.POST, request.FILES)
            
            if form.is_valid():
                
                # save ingredient data in DB
                ingredient = form.save(commit=False)
                ingredient.upload_state = 0
                ingredient.update_state = 0
                ingredient.reg_admin = request.user.id
                ingredient.reg_date = timezone.now()
                ingredient.save()

                ingdId = ingredient.ingd_id

                logInfo = ManageLog()
                logInfo.admin_id = request.user.id
                logInfo.job_code = JobInfo.JOB_ADD_INGREDIENT
                logInfo.job_name = JobInfo.JOBN_ADD_INGREDIENT
                logInfo.content_id = ingdId
                logInfo.content_type = ContentInfo.CONTENT_TYPE_INGREDIENT
                logInfo.save()
                
                # save img data
                imageFile = request.FILES.get('image_file', False)

                if imageFile == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    imgData = Image()
                    imgData.image_type = Image.IMG_TYPE_REP
                    imgData.content_id = ingdId
                    imgData.content_type = ContentInfo.CONTENT_TYPE_INGREDIENT
                    imgData.is_open = Image.IMG_STATUS_PUB
                    imgData.save()

                    # 2. 이미지 ID를 이용한 경로 생성
                    img_path = imageIdToPath(imgData.image_id)
                    saveImgToPath(imageFile, imgData.image_id, DATA_ROOT+ IMAGE_PATH + "/" + img_path + "/")

                    # DB에 이미지 경로 업데이트
                    imgData.path = img_path + "/" + str(imgData.image_id)
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

@api_view(['GET', 'POST'])
def equipment(request):
    
    if request.method == 'GET':
        return ""
        

    elif request.method == 'POST':
        respone = 'this is test response'
        

        # 도구 데이터 저장 + 이미지 저장 트랜잭션 처리
        with transaction.atomic():

            # validate data
            form = EquipmentForm(request.POST, request.FILES)
            
            if form.is_valid():
                
                # save equipment data in DB
                equipment = form.save(commit=False)
                equipment.upload_state = 0
                equipment.update_state = 0
                equipment.reg_admin = request.user.id
                equipment.reg_date = timezone.now()
                equipment.save()

                equipId = equipment.equip_id

                logInfo = ManageLog()
                logInfo.admin_id = request.user.id
                logInfo.job_code = JobInfo.JOB_ADD_EQUIP
                logInfo.job_name = JobInfo.JOBN_ADD_EQUIP
                logInfo.content_id = equipId
                logInfo.content_type = ContentInfo.CONTENT_TYPE_EQUIP
                logInfo.save()
                
                # save img data
                imageFile = request.FILES.get('image_file', False)

                if imageFile == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    imgData = Image()
                    imgData.image_type = Image.IMG_TYPE_REP
                    imgData.content_id = equipId
                    imgData.content_type = ContentInfo.CONTENT_TYPE_EQUIP
                    imgData.is_open = Image.IMG_STATUS_PUB
                    imgData.save()

                    # 2. 이미지 ID를 이용한 경로 생성
                    img_path = imageIdToPath(imgData.image_id)
                    saveImgToPath(imageFile, imgData.image_id, DATA_ROOT+ IMAGE_PATH + "/" + img_path + "/")

                    # DB에 이미지 경로 업데이트
                    imgData.path = img_path + "/" + str(imgData.image_id)
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


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def word(request):
    
    if request.method == 'GET':
        return ""
        

    elif request.method == 'POST':
        respone = 'this is test response'
        

        # 용어 데이터 저장 + 이미지 저장 트랜잭션 처리
        with transaction.atomic():

            # validate data
            form = WordForm(request.POST, request.FILES)
            
            if form.is_valid():
                
                # save word data in DB
                word = form.save(commit=False)
                #word.upload_state = 0
                #word.update_state = 0
                word.reg_admin = request.user.id
                word.reg_date = timezone.now()
                word.save()

                word_id = word.word_id

                log_info = ManageLog()
                log_info.admin_id = request.user.id
                log_info.job_code = JobInfo.JOB_ADD_WORD
                log_info.job_name = JobInfo.JOBN_ADD_WORD
                log_info.content_id = word_id
                log_info.content_type = ContentInfo.CONTENT_TYPE_WORD
                log_info.save()
                
                # save img data
                image_file = request.FILES.get('image_file', False)

                if image_file == False:
                    pass
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    img_data = Image()
                    img_data.image_type = Image.IMG_TYPE_REP
                    img_data.content_id = word_id
                    img_data.content_type = ContentInfo.CONTENT_TYPE_WORD
                    img_data.is_open = Image.IMG_STATUS_PUB
                    img_data.save()

                    # save image to DB
                    img_path = imageIdToPath(img_data.image_id)
                    saveImgToPath(image_file, img_data.image_id, DATA_ROOT+ IMAGE_PATH + "/" + img_path + "/")

                    # DB에 이미지 경로 업데이트
                    img_data.path = img_path + "/" + str(img_data.image_id)
                    img_data.save(update_fields=['path'])

                return Response(respone, status=status.HTTP_200_OK)
            else:
                print("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
        return Response(respone)


@api_view(['GET'])
def liquor_dup_chck(request):

    # name_kr, name_en 수신
    name_kr = request.GET.get('nameKr')
    name_en = request.GET.get('nameEn')

    # null and '' check
    # lowercase, remove whitespace
    if name_kr != None and len(name_kr) > 0:
        name_kr = name_kr.lower()
        name_kr = name_kr.replace(" ", "")
    else:
        name_kr = ""

    if name_en != None and len(name_en) > 0:
        name_en = name_en.lower()
        name_en = name_en.replace(" ", "")
    else:
        name_en = ""

    q = '''
        SELECT 
            liquor_id,
            name_kr,
            name_en
        FROM tipsy_raw.raw_liquor
        WHERE lower(replace(name_kr, ' ', '')) = '%s'
        OR lower(replace(name_en, ' ', '')) = '%s'        
    ''' % (name_kr, name_en)

    # db query
    dup_list = RawLiquor.objects.raw(q)
    serialized_dup_list = RawLiquorSerializer(dup_list, many=True) 
    
    # TODO: 이름 리스트만 반환 할 수 있도록 변경
    
    return Response(serialized_dup_list.data)

@api_view(['GET'])
def ingredient_dup_chck(request):

    # name_kr, name_en 수신
    name_kr = request.GET.get('nameKr')
    name_en = request.GET.get('nameEn')

    # null and '' check
    # lowercase, remove whitespace
    if name_kr != None and len(name_kr) > 0:
        name_kr = name_kr.lower()
        name_kr = name_kr.replace(" ", "")
    else:
        name_kr = ""

    if name_en != None and len(name_en) > 0:
        name_en = name_en.lower()
        name_en = name_en.replace(" ", "")
    else:
        name_en = ""

    q = '''
        SELECT 
            ingd_id,
            name_kr,
            name_en
        FROM tipsy_raw.ingredient
        WHERE lower(replace(name_kr, ' ', '')) = '%s'
        OR lower(replace(name_en, ' ', '')) = '%s'        
    ''' % (name_kr, name_en)

    # db query
    dup_list = Ingredient.objects.raw(q)
    serialized_dup_list = IngredientSerializer(dup_list, many=True) 
    
    # TODO: 이름 리스트만 반환 할 수 있도록 변경
    
    return Response(serialized_dup_list.data)


@api_view(['GET'])
def equipment_dup_chck(request):

    # name_kr, name_en 수신
    name_kr = request.GET.get('nameKr')
    name_en = request.GET.get('nameEn')

    # null and '' check
    # lowercase, remove whitespace
    if name_kr != None and len(name_kr) > 0:
        name_kr = name_kr.lower()
        name_kr = name_kr.replace(" ", "")
    else:
        name_kr = ""

    if name_en != None and len(name_en) > 0:
        name_en = name_en.lower()
        name_en = name_en.replace(" ", "")
    else:
        name_en = ""

    q = '''
        SELECT 
            equip_id,
            name_kr,
            name_en
        FROM tipsy_raw.equipment
        WHERE lower(replace(name_kr, ' ', '')) = '%s'
        OR lower(replace(name_en, ' ', '')) = '%s'        
    ''' % (name_kr, name_en)

    # db query
    dup_list = Equipment.objects.raw(q)
    serialized_dup_list = EquipmentSerializer(dup_list, many=True) 
    
    # TODO: 이름 리스트만 반환 할 수 있도록 변경
    
    return Response(serialized_dup_list.data)

@api_view(['GET'])
def word_dup_chck(request):

    # name_kr, name_en 수신
    name_kr = request.GET.get('nameKr')
    name_en = request.GET.get('nameEn')

    # null and '' check
    # lowercase, remove whitespace
    if name_kr != None and len(name_kr) > 0:
        name_kr = name_kr.lower()
        name_kr = name_kr.replace(" ", "")
    else:
        name_kr = ""

    if name_en != None and len(name_en) > 0:
        name_en = name_en.lower()
        name_en = name_en.replace(" ", "")
    else:
        name_en = ""

    q = '''
        SELECT 
            word_id,
            name_kr,
            name_en
        FROM tipsy_raw.word
        WHERE lower(replace(name_kr, ' ', '')) = '%s'
        OR lower(replace(name_en, ' ', '')) = '%s'        
    ''' % (name_kr, name_en)

    # db query
    dup_list = Word.objects.raw(q)
    serialized_dup_list = WordSerializer(dup_list, many=True) 
    
    # TODO: 이름 리스트만 반환 할 수 있도록 변경
    
    return Response(serialized_dup_list.data)

@api_view(['GET'])
def cocktail_dup_chck(request):

    # name_kr, name_en 수신
    name_kr = request.GET.get('nameKr')
    name_en = request.GET.get('nameEn')

    # null and '' check
    # lowercase, remove whitespace
    if name_kr != None and len(name_kr) > 0:
        name_kr = name_kr.lower()
        name_kr = name_kr.replace(" ", "")
    else:
        name_kr = ""

    if name_en != None and len(name_en) > 0:
        name_en = name_en.lower()
        name_en = name_en.replace(" ", "")
    else:
        name_en = ""

    q = '''
        SELECT 
            cocktail_id,
            name_kr,
            name_en
        FROM tipsy_raw.cocktail
        WHERE lower(replace(name_kr, ' ', '')) = '%s'
        OR lower(replace(name_en, ' ', '')) = '%s'        
    ''' % (name_kr, name_en)

    # db query
    dup_list = Cocktail.objects.raw(q)
    serialized_dup_list = CocktailSerializer(dup_list, many=True) 
    
    # TODO: 이름 리스트만 반환 할 수 있도록 변경
    
    return Response(serialized_dup_list.data)


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
       