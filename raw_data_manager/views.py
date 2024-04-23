from email.contentmanager import raw_data_manager
from re import L
from django.utils import timezone
from core.settings import DATA_ROOT, IMAGE_PATH, SVC_MGR_URL, S3_URL
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
from django.db.models import Q
from django.db import connection
import mimetypes
import PIL.Image as pilimg
import pytesseract
import easyocr
import os
import requests
import json
import logging
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger('django')

@api_view(['GET'])
def createPermissions(request):
    logger.info("[[Create Permissions ]]");
    # ORM을 이용한 관리자 권한 생성 - 수동으로 DB의 auth_permission 테이블에 추가해도 된다.
    # # equipment
    # content_type = ContentType.objects.get_for_model(Equipment)
    # permission = Permission.objects.create(
    #     codename='delete_equipment',
    #     name='Can Delete Equipment',
    #     content_type=content_type,
    # )
    # permission = Permission.objects.create(
    #     codename='modify_equipment',
    #     name='Can Modify Equipment',
    #     content_type=content_type,
    # )

    # # ingredient
    # content_type = ContentType.objects.get_for_model(Ingredient)
    # permission = Permission.objects.create(
    #     codename='delete_ingredient',
    #     name='Can Delete Ingredient',
    #     content_type=content_type,
    # )
    # permission = Permission.objects.create(
    #     codename='modify_ingredient',
    #     name='Can Modify Ingredient',
    #     content_type=content_type,
    # )

    # # cocktail
    # content_type = ContentType.objects.get_for_model(Cocktail)
    # permission = Permission.objects.create(
    #     codename='delete_cocktail',
    #     name='Can Delete Cocktail',
    #     content_type=content_type,
    # )
    # permission = Permission.objects.create(
    #     codename='modify_cocktail',
    #     name='Can Modify Cocktail',
    #     content_type=content_type,
    # )

    # # word
    # content_type = ContentType.objects.get_for_model(Word)
    # permission = Permission.objects.create(
    #     codename='delete_word',
    #     name='Can Delete Word',
    #     content_type=content_type,
    # )
    # permission = Permission.objects.create(
    #     codename='modify_word',
    #     name='Can Modify Word',
    #     content_type=content_type,
    # )

    return 'success'    

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
            search_url += '&paging.nowPage=%s'%nowPage

        pergPage = request.GET.get('perPage')
        if pergPage != None:
            search_url += '&paging.perPage=%s'%pergPage


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
@transaction.atomic
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
            image_file = request.FILES.get('image_file', False)

            if image_file == False:
                raise Exception("No Image File")
            else:
                try:
                    with transaction.atomic():

                        if image.image_type == Image.IMG_TYPE_REP:
                            # 기존에 존재하는 이미지중에 대표 이미지 조회 후 수정
                            try:
                                rep_img = Image.objects.get(image_type=Image.IMG_TYPE_REP, 
                                                        content_type=image.content_type,
                                                        content_id=image.content_id)
                                rep_img.image_type = Image.IMG_TYPE_NORMAL
                                rep_img.save(update_fields=['image_type'])
                            except Image.DoesNotExist as e:
                                pass
                                #logger.error("There is no rep_img.")  

                            # save image to DB
                            image.save()

                            # save image file
                            s3_key = saveImgToS3(image_file, 'image/liquor')

                            img = pilimg.open(image_file)
                            extension = img.format.lower()
            
                            # update image's path to DB
                            image.s3_key = s3_key
                            image.extension = extension
                            image.save(update_fields=['s3_key', 'extension'])
                        else:
                            image.save()

                            logger.info("[#### 신규 이미지 파일 타입 ###]")
                            logger.info(type(image_file))

                            # 2. save image to S3
                            s3_key = saveImgToS3(image_file, 'image/liquor')

                            img = pilimg.open(image_file)
                            extension = img.format.lower()

                            # 3. DB에 이미지 경로 업데이트
                            image.s3_key = s3_key
                            image.extension = extension
                            image.save(update_fields=['s3_key', 'extension'])

                        return Response("success")

                except Image.MultipleObjectsReturned as e:
                    logger.error("There is multiple rep_img. content_id:%s, content_type:%s" % (image.content_id, image.content_type)) # change to log...
        else:
            return Response("No Validated Request", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PUT':

        # 트랜잭션 처리
        # 대표로 지정된 경우 해당 컨텐츠의 다른 이미지를 불러와서
        # 일반 이미지로 변경한다.
        image_form = ImageForm(request.POST, request.FILES)        

        if image_form.is_valid():
            image = image_form.save(False)
            try:
                with transaction.atomic():

                    if image.image_type == Image.IMG_TYPE_REP:
                        # 기존에 존재하는 이미지중에 대표 이미지 조회 후 수정
                        try:
                            rep_img = Image.objects.get(image_type=Image.IMG_TYPE_REP, 
                                                    content_type=image.content_type,
                                                    content_id=image.content_id)
                            rep_img.image_type = Image.IMG_TYPE_NORMAL
                            rep_img.save(update_fields=['image_type'])
                        except Image.DoesNotExist:  # 이미지가 존재하지 않는 경우
                            # 에러 처리 코드 작성
                            pass
                    else:
                        images = Image.objects.filter(
                                                    content_id=image.content_id,
                                                    content_type=image.content_type,    
                                                    image_type=Image.IMG_TYPE_NORMAL                   
                                                )

                        if len(images) <= 0:
                            return Response("Last image can't change to normal type.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
                        for other in images:
                            if other.image_id != image.image_id:
                                other.image_type = Image.IMG_TYPE_REP
                                other.save(update_fields=['image_type'])
                                break 
                        
                    image.save(update_fields=['image_type', 'is_open'])
                    return Response("success")

            except Image.MultipleObjectsReturned as e:
                logger.error("There is multiple rep_img. content_id:%s, content_type:%s" % (image.content_id, image.content_type)) # change to log...
        else:
            return Response("No Validated Request", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response("This is image PUT return")

    elif request.method == 'DELETE':
        req_data = ImageForm(request.POST)

        if req_data.is_valid():

            # 트랜잭션
            with transaction.atomic():

                image_id = req_data.cleaned_data['image_id']

                if image_id is None and image_id <= 0:
                    return Response("No Validated Image ID", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # DB 데이터 제거
                img_data = Image.objects.get(pk=image_id)

                # 대표 이미지라면 다른 이미지를 대표 이미지로 설정
                if img_data.image_type == Image.IMG_TYPE_REP:
                    images = Image.objects.filter(
                                                content_id=img_data.content_id,
                                                content_type=img_data.content_type,
                                                image_type=Image.IMG_TYPE_NORMAL                   
                                            )

                    if len(images) <= 0:
                        return Response("Last image can't delete.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
                    for image in images:
                        if image.image_id != image_id:
                            image.image_type = Image.IMG_TYPE_REP
                            image.save(update_fields=['image_type'])
                            break
                
                s3_key = img_data.s3_key
                img_data.delete()

                # 이미지 s3 객체 제거 
                deleteObjectFromS3(s3_key)

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

        liquor_id = int(request.GET.get('liquorId', 0))

        logger.info("liquor_id: %d" % liquor_id)

        if liquor_id == 0:
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        # page = int(request.GET.get('page', 1))
        # perPage = int(request.GET.get('perPage', 10))
        # totalCount = RawLiquor.objects.all().count()    # TODO: 비효율적인 코드

        # pageInfo = Paging(page,totalCount,perPage)
        # pages = pageInfo.getPages()
        # firstRow = pageInfo.getFirstRow()

        # # #liquorList = RawLiquor.objects.order_by('-liquor_id')[firstRow:firstRow+perPage].values()
        # # liquorList = list(RawLiquor.objects.order_by('-liquor_id')[firstRow:firstRow+perPage].values())
        # # serializer = RawLiquorSerializer(liquorList, many=True) 

    
        # # TODO: join에 대한 내용을 model에 반영해서 조회하기
        # liquorList = JoinedLiquor.objects.order_by('-liquor_id').raw('''
        #     SELECT 
        #         raw_liquor.*,
        #         categ1.name as category1_name,
        #         categ2.name as category2_name,
        #         categ3.name as category3_name,
        #         categ4.name as category4_name,
        #         country.name as country_name,
        #         reg_user.username as reg_admin_name,
        #         update_user.username as update_admin_name,
        #         if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        #     FROM tipsy_raw.raw_liquor
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = raw_liquor.category1_id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = raw_liquor.category2_id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = raw_liquor.category3_id
        #     LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = raw_liquor.category4_id
        #     LEFT OUTER JOIN tipsy_raw.country ON country.country_id = raw_liquor.country_id
        #     LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = raw_liquor.reg_admin
        #     LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = raw_liquor.update_admin
        #     LEFT OUTER JOIN image ON image.content_id = raw_liquor.liquor_id AND image.content_type = 100 AND image.image_type = 0
        # ''')


        # paginator = Paginator(liquorList, perPage)  # 페이지당 10개씩 보여주기
        # page_obj = paginator.get_page(page)

        # serializer = JoinedLiquorSerializer(page_obj, many=True) 
        # #serializer = JoinedLiquorSerializer(liquorList, many=True) 
     
        # # TODO: 페이징 정보와 함께 묶어서 Serialize 해주고싶지만 하지못함
        # #sParam = SearchParam()
        # #sParam.list = liquorList
        # #res = cserializers.serialize("json", paramList)
        # #res = json.dumps(sParam, cls=DjangoJSONEncoder)
        # #res = json.dumps(sParam.paging.__dict__, default=str)
        
        # return Response(serializer.data)

        select_qry =  'SELECT '
        select_qry += ' raw_liquor.*, '
        select_qry += ' categ1.name as category1_name, '
        select_qry += ' categ2.name as category2_name, '
        select_qry += ' categ3.name as category3_name, '
        select_qry += ' categ4.name as category4_name, '
        select_qry += ' country.name as country_name, '
        select_qry += ' reg_user.username as reg_admin_name, '
        select_qry += ' update_user.username as update_admin_name, '
        select_qry += ' if(image.s3_key is null, "image/liquor/default_image.png", image.s3_key) as s3_key '
        select_qry += 'FROM raw_liquor '
        select_qry += 'LEFT OUTER JOIN raw_category categ1 ON categ1.id = raw_liquor.category1_id '
        select_qry += 'LEFT OUTER JOIN raw_category categ2 ON categ2.id = raw_liquor.category2_id '
        select_qry += 'LEFT OUTER JOIN raw_category categ3 ON categ3.id = raw_liquor.category3_id '
        select_qry += 'LEFT OUTER JOIN raw_category categ4 ON categ4.id = raw_liquor.category4_id '
        select_qry += 'LEFT OUTER JOIN country ON country.country_id = raw_liquor.country_id '
        select_qry += 'LEFT OUTER JOIN auth_user reg_user ON reg_user.id = raw_liquor.reg_admin '
        select_qry += 'LEFT OUTER JOIN auth_user update_user ON update_user.id = raw_liquor.update_admin '
        select_qry += 'LEFT OUTER JOIN image ON image.content_id = raw_liquor.liquor_id AND image.content_type = 100 AND image.image_type = 0 '
        select_qry += 'WHERE raw_liquor.liquor_id = %d' % liquor_id

        liquor = JoinedLiquor.objects.raw(select_qry)[0]
        
        serializer = JoinedLiquorSerializer(liquor, many=False)
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

                # content stats
                content_stats = ContentStats()
                content_stats.content_id = liquorId
                content_stats.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
                content_stats.save()

                # rating stats
                rating_stats = RatingStats()
                rating_stats.content_id = liquorId
                rating_stats.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
                rating_stats.save()


                log_info = ManageLog()
                log_info.admin_id = request.user.id
                log_info.job_code = JobInfo.JOB_ADD_SPIRITS
                log_info.job_name = JobInfo.JOBN_ADD_SPIRITS
                log_info.content_id = liquorId
                log_info.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
                log_info.save()
                
                # save img data
                image_file = request.FILES.get('image_file', False)

                if image_file == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    img_data = Image()
                    img_data.image_type = Image.IMG_TYPE_REP
                    img_data.content_id = liquorId
                    img_data.content_type = ContentInfo.CONTENT_TYPE_LIQUOR
                    img_data.is_open = Image.IMG_STATUS_PUB
                    img_data.save()

                    # 2. save image to S3
                    s3_key = saveImgToS3(image_file, 'image/liquor')

                    img = pilimg.open(image_file)
                    extension = img.format.lower()

                    # 3. DB에 이미지 경로 업데이트
                    img_data.s3_key = s3_key
                    img_data.extension = extension
                    img_data.save(update_fields=['s3_key', 'extension'])


                    # 임시 파일 저장 이름
                    #length_of_string = 8
                    #tmpName = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))

                return Response(respone, status=status.HTTP_200_OK)
            else:
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    elif request.method == 'PUT':

        perm = request.user.has_perm('raw_data_manager.modify_liquor')
        if perm == False:
            return Response("No Permission", status=status.HTTP_403_FORBIDDEN)

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
            
            # upload_state
            if prev_liquor.upload_state != liquor.upload_state:
                prev_info['upload_state'] = prev_liquor.upload_state
                updated_info['upload_state'] = liquor.upload_state
                prev_liquor.upload_state = liquor.upload_state

            # update_state
            if prev_liquor.update_state != liquor.update_state:
                prev_info['update_state'] = prev_liquor.update_state
                updated_info['update_state'] = liquor.update_state
                prev_liquor.update_state = liquor.update_state

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

            # _region
            if prev_liquor.region != liquor.region:
                prev_info['region'] = prev_liquor.region
                updated_info['region'] = liquor.region
                prev_liquor.region = liquor.region

            # _region_id
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
                if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
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
                image_file = request.FILES.get('image_file', False)

                if image_file == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    img_data = Image()
                    img_data.image_type = Image.IMG_TYPE_REP
                    img_data.content_id = cocktailId
                    img_data.content_type = ContentInfo.CONTENT_TYPE_COCTAIL
                    img_data.is_open = Image.IMG_STATUS_PUB
                    img_data.save()

                    # 2. save image to S3
                    s3_key = saveImgToS3(image_file, 'image/cocktail')

                    img = pilimg.open(image_file)
                    extension = img.format.lower()

                    # 3. DB에 이미지 경로 업데이트
                    img_data.s3_key = s3_key
                    img_data.extension = extension
                    img_data.save(update_fields=['s3_key', 'extension'])

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
        
        # check permission
        perm = request.user.has_perm('raw_data_manager.modify_cocktail')
        if perm == False:
            return Response("No Permission", status=status.HTTP_403_FORBIDDEN)


        pass

    elif request.method == 'DELETE':
        
        # check permission
        perm = request.user.has_perm('raw_data_manager.delete_cocktail')
        if perm == False:
            return Response("No Permission", status=status.HTTP_403_FORBIDDEN)


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

                    
                    # content stats
                    content_stats = ContentStats()
                    content_stats.content_id = cocktail_id
                    content_stats.content_type = ContentInfo.CONTENT_TYPE_COCTAIL
                    content_stats.save()

                    # rating stats
                    rating_stats = RatingStats()
                    rating_stats.content_id = cocktail_id
                    rating_stats.content_type = ContentInfo.CONTENT_TYPE_COCTAIL
                    rating_stats.save()

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




@api_view(['GET', 'POST', 'PUT', 'DELETE'])
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
                image_file = request.FILES.get('image_file', False)

                if image_file == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    img_data = Image()
                    img_data.image_type = Image.IMG_TYPE_REP
                    img_data.content_id = ingdId
                    img_data.content_type = ContentInfo.CONTENT_TYPE_INGREDIENT
                    img_data.is_open = Image.IMG_STATUS_PUB
                    img_data.save()

                    # 2. save image to S3
                    s3_key = saveImgToS3(image_file, 'image/ingredient')

                    img = pilimg.open(image_file)
                    extension = img.format.lower()

                    # 3. DB에 이미지 경로 업데이트
                    img_data.s3_key = s3_key
                    img_data.extension = extension
                    img_data.save(update_fields=['s3_key', 'extension'])

                return Response(respone, status=status.HTTP_200_OK)
            else:
                print("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
        return Response(respone)

    elif request.method == 'PUT':
        
        # check permission
        perm = request.user.has_perm('raw_data_manager.modify_ingredient')
        if perm == False:
            return Response("No Permission", status=status.HTTP_403_FORBIDDEN)

        logger.info(request.POST)

        form = IngredientForm(request.POST)
        
        if form.is_valid():
            updated_ingd = form.save(commit=False)            
            
            ingd_id = updated_ingd.ingd_id

            logger.debug("updated ingredient id: %s"% id)

            # 변경 내용 확인
            prev_ingd = Ingredient.objects.get(ingd_id=ingd_id)

            prev_info = {}
            updated_info = {}

            # name_kr
            if prev_ingd.name_kr != updated_ingd.name_kr:
                prev_info['name_kr'] = prev_ingd.name_kr
                updated_info['name_kr'] = updated_ingd.name_kr
                prev_ingd.name_kr = updated_ingd.name_kr
            
            # name_en
            if prev_ingd.name_en != updated_ingd.name_en:
                prev_info['name_en'] = prev_ingd.name_en
                updated_info['name_en'] = updated_ingd.name_en
                prev_ingd.name_en = updated_ingd.name_en
            
            # upload_state
            if prev_ingd.upload_state != updated_ingd.upload_state:
                prev_info['upload_state'] = prev_ingd.upload_state
                updated_info['upload_state'] = updated_ingd.upload_state
                prev_ingd.upload_state = updated_ingd.upload_state

            # update_state
            if prev_ingd.update_state != updated_ingd.update_state:
                prev_info['update_state'] = prev_ingd.update_state
                updated_info['update_state'] = updated_ingd.update_state
                prev_ingd.update_state = updated_ingd.update_state

            # category1_id
            if prev_ingd.category1_id != updated_ingd.category1_id:
                prev_info['category1_id'] = prev_ingd.category1_id
                updated_info['category1_id'] = updated_ingd.category1_id
                prev_ingd.category1_id = updated_ingd.category1_id

            # category2_id
            if prev_ingd.category2_id != updated_ingd.category2_id:
                prev_info['category2_id'] = prev_ingd.category2_id
                updated_info['category2_id'] = updated_ingd.category2_id
                prev_ingd.category2_id = updated_ingd.category2_id

            # category3_id
            if prev_ingd.category3_id != updated_ingd.category3_id:
                prev_info['category3_id'] = prev_ingd.category3_id
                updated_info['category3_id'] = updated_ingd.category3_id
                prev_ingd.category3_id = updated_ingd.category3_id

            # category4_id
            if prev_ingd.category4_id != updated_ingd.category4_id:
                prev_info['category4_id'] = prev_ingd.category4_id
                updated_info['category4_id'] = updated_ingd.category4_id
                prev_ingd.category4_id = updated_ingd.category4_id

            # description
            if prev_ingd.description != updated_ingd.description:
                prev_info['description'] = prev_ingd.description
                updated_info['description'] = updated_ingd.description
                prev_ingd.description = updated_ingd.description

            prev_ingd.update_state = ContentInfo.UPDATE_STATE_NEED_CONFIRM
            prev_ingd.update_admin = request.user.id
            prev_ingd.update_date = timezone.now()
            prev_ingd.save(update_fields=['name_kr', 'name_en', 'description', 'upload_state', 'update_state', 'update_admin',
                                        'update_date', 'category1_id', 'category2_id', 'category3_id', 'category4_id'])

            info = {
                "prev_info": prev_info,
                "updated_info": updated_info
            }
            info_str = json.dumps(info, ensure_ascii=False)
            
            # content stats
            content_stats = ContentStats()
            content_stats.content_id = ingd_id
            content_stats.content_type = ContentInfo.CONTENT_TYPE_INGREDIENT
            content_stats.save()

            # rating stats
            rating_stats = RatingStats()
            rating_stats.content_id = ingd_id
            rating_stats.content_type = ContentInfo.CONTENT_TYPE_INGREDIENT
            rating_stats.save()

            logInfo = ManageLog()
            logInfo.admin_id = request.user.id
            logInfo.job_code = JobInfo.JOB_MODIFY_INGREDIENT
            logInfo.job_name = JobInfo.JOBN_MODIFY_INGREDIENT
            logInfo.content_id = ingd_id
            logInfo.info = info_str
            logInfo.content_type = ContentInfo.CONTENT_TYPE_INGREDIENT
            logInfo.save()
            return Response("success", status=status.HTTP_200_OK)
        else:
            print("No Validated")
            # TODO: return error response
            return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
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

                equip_id = equipment.equip_id
            
                # content stats
                content_stats = ContentStats()
                content_stats.content_id = equip_id
                content_stats.content_type = ContentInfo.CONTENT_TYPE_EQUIP
                content_stats.save()

                # rating stats
                rating_stats = RatingStats()
                rating_stats.content_id = equip_id
                rating_stats.content_type = ContentInfo.CONTENT_TYPE_EQUIP
                rating_stats.save()

                logInfo = ManageLog()
                logInfo.admin_id = request.user.id
                logInfo.job_code = JobInfo.JOB_ADD_EQUIP
                logInfo.job_name = JobInfo.JOBN_ADD_EQUIP
                logInfo.content_id = equip_id
                logInfo.content_type = ContentInfo.CONTENT_TYPE_EQUIP
                logInfo.save()
                
                # save img data
                image_file = request.FILES.get('image_file', False)

                if image_file == False:
                    raise Exception("No Image File")
                else:          
                    
                    # 1. 이미지 데이터 DB 저장
                    img_data = Image()
                    img_data.image_type = Image.IMG_TYPE_REP
                    img_data.content_id = equip_id
                    img_data.content_type = ContentInfo.CONTENT_TYPE_EQUIP
                    img_data.is_open = Image.IMG_STATUS_PUB
                    img_data.save()

                    # 2. save image to S3
                    s3_key = saveImgToS3(image_file, 'image/liquor')

                    img = pilimg.open(image_file)
                    extension = img.format.lower()

                    # 3. DB에 이미지 경로 업데이트
                    img_data.s3_key = s3_key
                    img_data.extension = extension
                    img_data.save(update_fields=['s3_key', 'extension'])

                return Response(respone, status=status.HTTP_200_OK)
            else:
                print("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
        return Response(respone)
    
    elif request.method == 'PUT':


        # check permission
        perm = request.user.has_perm('raw_data_manager.modify_equipment')
        if perm == False:
            return Response("No Permission", status=status.HTTP_403_FORBIDDEN)


        logger.info(request.POST)

        form = EquipmentForm(request.POST)
        
        if form.is_valid():
            
            updated_equip = form.save(commit=False)            
            
            equip_id = updated_equip.equip_id

            logger.debug("updated equipment id: %s"% id)

            # 변경 내용 확인
            prev_equip = Equipment.objects.get(equip_id=equip_id)

            prev_info = {}
            updated_info = {}

            # name_kr
            if prev_equip.name_kr != updated_equip.name_kr:
                prev_info['name_kr'] = prev_equip.name_kr
                updated_info['name_kr'] = updated_equip.name_kr
                prev_equip.name_kr = updated_equip.name_kr
            
            # name_en
            if prev_equip.name_en != updated_equip.name_en:
                prev_info['name_en'] = prev_equip.name_en
                updated_info['name_en'] = updated_equip.name_en
                prev_equip.name_en = updated_equip.name_en
            
            # upload_state
            if prev_equip.upload_state != updated_equip.upload_state:
                prev_info['upload_state'] = prev_equip.upload_state
                updated_info['upload_state'] = updated_equip.upload_state
                prev_equip.upload_state = updated_equip.upload_state

            # update_state
            if prev_equip.update_state != updated_equip.update_state:
                prev_info['update_state'] = prev_equip.update_state
                updated_info['update_state'] = updated_equip.update_state
                prev_equip.update_state = updated_equip.update_state

            # category1_id
            if prev_equip.category1_id != updated_equip.category1_id:
                prev_info['category1_id'] = prev_equip.category1_id
                updated_info['category1_id'] = updated_equip.category1_id
                prev_equip.category1_id = updated_equip.category1_id

            # category2_id
            if prev_equip.category2_id != updated_equip.category2_id:
                prev_info['category2_id'] = prev_equip.category2_id
                updated_info['category2_id'] = updated_equip.category2_id
                prev_equip.category2_id = updated_equip.category2_id

            # category3_id
            if prev_equip.category3_id != updated_equip.category3_id:
                prev_info['category3_id'] = prev_equip.category3_id
                updated_info['category3_id'] = updated_equip.category3_id
                prev_equip.category3_id = updated_equip.category3_id

            # category4_id
            if prev_equip.category4_id != updated_equip.category4_id:
                prev_info['category4_id'] = prev_equip.category4_id
                updated_info['category4_id'] = updated_equip.category4_id
                prev_equip.category4_id = updated_equip.category4_id

            # description
            if prev_equip.description != updated_equip.description:
                prev_info['description'] = prev_equip.description
                updated_info['description'] = updated_equip.description
                prev_equip.description = updated_equip.description

            prev_equip.update_state = ContentInfo.UPDATE_STATE_NEED_CONFIRM
            prev_equip.update_admin = request.user.id
            prev_equip.update_date = timezone.now()
            prev_equip.save(update_fields=['name_kr', 'name_en', 'description', 'upload_state', 'update_state', 'update_admin',
                                        'update_date', 'category1_id', 'category2_id', 'category3_id', 'category4_id'])

            info = {
                "prev_info": prev_info,
                "updated_info": updated_info
            }
            info_str = json.dumps(info, ensure_ascii=False)

            log_info = ManageLog()
            log_info.admin_id = request.user.id
            log_info.job_code = JobInfo.JOB_MODIFY_EQUIP
            log_info.job_name = JobInfo.JOBN_MODIFY_EQUIP
            log_info.content_id = equip_id
            log_info.info = info_str
            log_info.content_type = ContentInfo.CONTENT_TYPE_EQUIP
            log_info.save()
            return Response("success", status=status.HTTP_200_OK)
    

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
                word.reg_admin = request.user.id
                word.reg_date = timezone.now()
                word.save()

                word_id = word.word_id
                
                # content stats
                content_stats = ContentStats()
                content_stats.content_id = word_id
                content_stats.content_type = ContentInfo.CONTENT_TYPE_WORD
                content_stats.save()

                # rating stats
                rating_stats = RatingStats()
                rating_stats.content_id = word_id
                rating_stats.content_type = ContentInfo.CONTENT_TYPE_WORD
                rating_stats.save()

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

                    img = pilimg.open(image_file)
                    extension = img.format.lower()

                    # save image to S3
                    s3_key = saveImgToS3(image_file, 'image/word')

                    # DB에 이미지 경로 업데이트
                    img_data.s3_key = s3_key
                    img_data.extension = extension
                    img_data.save(update_fields=['s3_key', 'extension'])

                return Response(respone, status=status.HTTP_200_OK)
            else:
                print("No Validated")
                # TODO: return error response
                return Response("No Validated Data", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
        return Response(respone)
    
    elif request.method == 'PUT':
        
        # check permission
        perm = request.user.has_perm('raw_data_manager.modify_word')
        if perm == False:
            return Response("No Permission", status=status.HTTP_403_FORBIDDEN)


        logger.info(request.POST)

        form = WordForm(request.POST)
        
        if form.is_valid():
            
            updated_word = form.save(commit=False)            
            
            word_id = updated_word.word_id

            logger.debug("updated word id: %s"% id)

            # 변경 내용 확인
            prev_word = Word.objects.get(word_id=word_id)

            prev_info = {}
            updated_info = {}

            # name_kr
            if prev_word.name_kr != updated_word.name_kr:
                prev_info['name_kr'] = prev_word.name_kr
                updated_info['name_kr'] = updated_word.name_kr
                prev_word.name_kr = updated_word.name_kr
            
            # name_en
            if prev_word.name_en != updated_word.name_en:
                prev_info['name_en'] = prev_word.name_en
                updated_info['name_en'] = updated_word.name_en
                prev_word.name_en = updated_word.name_en
            
            # description
            if prev_word.description != updated_word.description:
                prev_info['description'] = prev_word.description
                updated_info['description'] = updated_word.description
                prev_word.description = updated_word.description

            prev_word.update_state = ContentInfo.UPDATE_STATE_NEED_CONFIRM
            prev_word.update_admin = request.user.id
            prev_word.update_date = timezone.now()
            prev_word.save(update_fields=['name_kr', 'name_en', 'description', 'update_admin', 'update_date'])

            info = {
                "prev_info": prev_info,
                "updated_info": updated_info
            }
            info_str = json.dumps(info, ensure_ascii=False)

            log_info = ManageLog()
            log_info.admin_id = request.user.id
            log_info.job_code = JobInfo.JOB_MODIFY_WORD
            log_info.job_name = JobInfo.JOBN_MODIFY_WORD
            log_info.content_id = word_id
            log_info.info = info_str
            log_info.content_type = ContentInfo.CONTENT_TYPE_WORD
            log_info.save()
            return Response("success", status=status.HTTP_200_OK)


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

@api_view(['PUT'])
def crawled_liquor_image(request):
    
    if request.method == 'PUT':
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
    else:
       pass 


@api_view(['GET'])
def crawled_liquor_image_list(request):
    
    if request.method == 'GET':

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('perPage', 10))
        offset = (page - 1) * per_page
        order_by_field = 'id'
        ascending = False

        liquor_id = int(request.GET.get('liquorId', 0))
        is_use = request.GET.get('isUse', None)

        if liquor_id == 0:
            return Response('Not founded data.')

        # set liquor_id filter
        queryset = CrawledLiquorImage.objects.filter(liquor_id=liquor_id)

        # set is_use filter
        if is_use is not None:
            is_use = int(is_use)
            if  is_use >= 0 and is_use < 3:
                queryset = queryset.filter(is_use=is_use)

        # set order_by, offset, limit
        queryset = queryset.order_by(f'{order_by_field}' if ascending else f'-{order_by_field}')[offset:offset+per_page]

        serialized = CrawledLiquorImageSerializer(queryset, many=True) 

        return Response(serialized.data)
    else:
       pass 
       

@api_view(['GET'])
def ocr(request):
    
    print("[OCR TEST]")

    # img_id = request.GET.get('imageId')
    # img_id = int(img_id)

    # logger.info("[OCR TEST] image_id: %d" % img_id)

    # if img_id == None:
    #     return Response("Not Found Image.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    # image = Image.objects.get(image_id=img_id)
    # path = image.path

    filename = request.GET.get('filename')

    print("[OCR TEST] filename: %s" % filename)

    reader = easyocr.Reader(['en', 'ko'], gpu=False)    
    #result = reader.readtext('/data/datastore/image'+'/'+path+'.png')
    result = reader.readtext('/Users/GwangA/datastore/tmp/' + filename)

    logger.info("[OCR TEST] find file")
    
    candidate_list = []
    logger.info("\n\n================ High Score ================\n")
    for item in result:
        confidence = item[2]
        if confidence >= 0.6:
            logger.info("%s => %s" % (item[1], item[2]))
            logger.info("\n")    
            candidate = {
                "word": item[1],
                "weight": item[2]
            }
            candidate_list.append(candidate)     

    res = {
        "candidate": candidate_list
    }          

    #return Response(json.dumps(res, ensure_ascii=False))
    return Response(res)
            
    # logger.info("================ All Score ================\n")
    # for item in result:
    #     confidence = item[2]
    #     logger.info("%s => %s" % (item[1], item[2]))
    #     logger.info("\n")


@api_view(['GET'])
def recommand(request):
    
    print("[Recommnad Liquor Test]")

    categ1_id = request.GET.get('categ1Id')
    categ2_id = request.GET.get('categ2Id')
    categ3_id = request.GET.get('categ3Id')
    categ4_id = request.GET.get('categ4Id')
    price_min = request.GET.get('priceMin')
    price_max = request.GET.get('priceMax')
    abv_min = request.GET.get('abvMin')
    abv_max = request.GET.get('abvMax')
    age = request.GET.get('age')
    pop = request.GET.get('pop')
    
    logger.info("categ1_id => %s" % (categ1_id))
    logger.info("categ2_id => %s" % (categ2_id))
    logger.info("categ3_id => %s" % (categ3_id))
    logger.info("categ4_id => %s" % (categ4_id))
    logger.info("price_min => %s" % (price_min))
    logger.info("price_max => %s" % (price_max))
    logger.info("abv_min => %s" % (abv_min))
    logger.info("abv_max => %s" % (abv_max))
    logger.info("age => %s" % (age))
    logger.info("pop => %s" % (pop))

    recommand_url = SVC_MGR_URL + "/api/recommand/liquor.tipsy?t=tipsy"

    
    if categ1_id != None:
        recommand_url += '&categ1Id=%s'%categ1_id

    if categ2_id != None:
        recommand_url += '&categ2Id=%s'%categ2_id

    if categ3_id != None:
        recommand_url += '&categ3Id=%s'%categ3_id

    if categ4_id != None:
        recommand_url += '&categ4Id=%s'%categ4_id
    
    if price_min != None:
        recommand_url += '&priceMin=%s'%price_min
            
    if price_max != None:
        recommand_url += '&priceMax=%s'%price_max
            
    if abv_min != None:
        recommand_url += '&abvMin=%s'%abv_min
            
    if abv_max != None:
        recommand_url += '&abvMax=%s'%abv_max
            
    if pop != None:
        recommand_url += '&pop=%s'%pop
            
    if age != None:
        recommand_url += '&age=%s'%age

    try:
        recommand_request = requests.get(recommand_url)
        print("\n[status]:%s"%recommand_request.status_code)
        print("\n[url]:%s"%recommand_request.url)
        if recommand_request.status_code == 200:
            return Response(recommand_request.text)
        else:
            return Response("ERROR!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except:
        return Response("ERROR!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    #return Response(json.dumps(res, ensure_ascii=False))
    
            