# -*- encoding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from django.db import connection

from django.shortcuts import get_object_or_404

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

import io
import json
import logging

from raw_data_manager.forms import *
from raw_data_manager.models import *
from raw_data_manager.serializers import *

logger = logging.getLogger('django')

@login_required(login_url="/admin/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'
    # context['prefix'] = 'http://211.37.150.105:8000'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

#@login_required(login_url="/login/")
def pages(request):

    context = {}
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/admin/login/")
def liquorList(request):
    
    context = {}
    context['segment'] = 'list_liquor'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # load data
    keyword = request.GET.get('keyword', "")
    keyword = '%%' + keyword + '%%'
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))


    print(keyword)

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
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
    #     WHERE raw_liquor.name_kr like %s or raw_liquor.name_en like %%s%
    #     ORDER BY liquor_id DESC
    # ''' % keyword, keyword)

    liquorList = JoinedLiquor.objects.order_by('-liquor_id').raw("" +
        "SELECT "+
        "    raw_liquor.*, "+
        "    categ1.name as category1_name, "+
        "    categ2.name as category2_name, "+
        "    categ3.name as category3_name, "+
        "    categ4.name as category4_name, "+
        "    country.name as country_name, "+
        "    reg_user.username as reg_admin_name, "+
        "    update_user.username as update_admin_name, "+
        "    if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key "+
        "FROM tipsy_raw.raw_liquor "+
        "LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = raw_liquor.category1_id "+
        "LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = raw_liquor.category2_id "+
        "LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = raw_liquor.category3_id "+
        "LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = raw_liquor.category4_id "+
        "LEFT OUTER JOIN tipsy_raw.country ON country.country_id = raw_liquor.country_id "+
        "LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = raw_liquor.reg_admin "+
        "LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = raw_liquor.update_admin "+
        "LEFT OUTER JOIN image ON image.content_id = raw_liquor.liquor_id AND image.content_type = 100 AND image.image_type = 0 "+
        "WHERE raw_liquor.name_kr like '" + keyword + "' or raw_liquor.name_en like '" + keyword + "' " +
        "ORDER BY liquor_id DESC")

    paginator = Paginator(liquorList, perPage)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context['liquor_list'] = page_obj
    keyword = keyword.replace('%', '')
    context['keyword'] = keyword

    html_template = loader.get_template( 'list_liquor.html' )
    return HttpResponse(html_template.render(context, request))




@login_required(login_url="/admin/login/")
def modifyLiquor(request):
   
    context = {}
    context['segment'] = 'modifyLiquor'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # check permission
    # perm = request.user.has_perm('raw_data_manager.modify_liquor')
    # if perm == False:
    #     html_template = loader.get_template( 'page-403.html' )
    #     return HttpResponse(html_template.render(context, request))


    # load data
    liquorId = request.GET.get('liquorId')

    if liquorId == None or liquorId == 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    else:
        liquorId = int(liquorId)

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    liquor = JoinedLiquor.objects.order_by('-liquor_id').raw('''
        SELECT 
            raw_liquor.*,
            categ1.name as category1_name,
            categ2.name as category2_name,
            categ3.name as category3_name,
            categ4.name as category4_name,
            country.name as country_name,
            reg_user.username as reg_admin_name, 
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.raw_liquor
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = raw_liquor.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = raw_liquor.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = raw_liquor.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = raw_liquor.category4_id
        LEFT OUTER JOIN tipsy_raw.country ON country.country_id = raw_liquor.country_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = raw_liquor.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = raw_liquor.update_admin
        LEFT OUTER JOIN image ON image.content_id = raw_liquor.liquor_id AND image.content_type = 100 AND image.image_type = 0
        WHERE raw_liquor.liquor_id = %d
    ''' % liquorId)

    if liquor == None:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    
    serialize_liquor = JoinedLiquorSerializer(liquor[0]) 
    liquor_bjson = JSONRenderer().render(serialize_liquor.data)    
    stream = io.BytesIO(liquor_bjson)
    liquor_dict = JSONParser().parse(stream)    
    liquor_json = json.dumps(liquor_dict, ensure_ascii=False)
    context['liquor'] = liquor_json

    log_obj = ManageLog.objects.get(id=83)
    log_bjson = JSONRenderer().render(ManageLogSerializer(log_obj).data)    
    log_stream = io.BytesIO(log_bjson)
    log_dict = JSONParser().parse(log_stream)    
    log_json = json.dumps(log_dict, ensure_ascii=False)
    context['log'] = log_json

    # get images
    images = Image.objects.filter(content_type=ContentInfo.CONTENT_TYPE_LIQUOR, content_id=liquor[0].liquor_id)   
    serialize_images = ImageSerializer(images, many=True)     
    images_bjson = JSONRenderer().render(serialize_images.data)    
    images_stream = io.BytesIO(images_bjson)
    images_dict = JSONParser().parse(images_stream)    
    images_json = json.dumps(images_dict, ensure_ascii=False)
    context['images'] = images_json

    html_template = loader.get_template( 'modify_liquor.html' )   
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/admin/login/")
def ingredientList(request):
    
    context = {}
    context['segment'] = 'list_ingredient'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # load data
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    ingredientList = JoinedIngredient.objects.order_by('-ingd_id').raw('''
        SELECT 
            ingredient.*,
            categ1.name as category1_name,
            categ2.name as category2_name,
            categ3.name as category3_name,
            categ4.name as category4_name,
            reg_user.username as reg_admin_name,
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.ingredient
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = ingredient.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = ingredient.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = ingredient.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = ingredient.category4_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = ingredient.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = ingredient.update_admin
        LEFT OUTER JOIN image ON image.content_id = ingredient.ingd_id AND image.content_type = 300 AND image.image_type = 0
        ORDER BY ingd_id DESC
    ''')

    paginator = Paginator(ingredientList, perPage)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context['ingredient_list'] = page_obj

    html_template = loader.get_template( 'list_ingredient.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def equipmentList(request):
    
    context = {}
    context['segment'] = 'list_equipment'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # load data
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    equipmentList = JoinedEquipment.objects.order_by('-equip_id').raw('''
        SELECT 
            equipment.*,
            categ1.name as category1_name,
            categ2.name as category2_name,
            categ3.name as category3_name,
            categ4.name as category4_name,
            reg_user.username as reg_admin_name,
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.equipment
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = equipment.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = equipment.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = equipment.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = equipment.category4_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = equipment.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = equipment.update_admin
        LEFT OUTER JOIN image ON image.content_id = equipment.equip_id AND image.content_type = 400 AND image.image_type = 0
        ORDER BY equip_id DESC
    ''')

    paginator = Paginator(equipmentList, perPage)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context['equipment_list'] = page_obj

    html_template = loader.get_template( 'list_equipment.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def modifyIngredient(request):
    
    #logger.debug("This is modifyIngredient View ... ")

    context = {}
    context['segment'] = 'modifyIngredient'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # check permission
    # perm = request.user.has_perm('raw_data_manager.modify_ingredient')
    # if perm == False:
    #     html_template = loader.get_template( 'page-403.html' )
    #     return HttpResponse(html_template.render(context, request))

    # load data
    ingdId = request.GET.get('ingdId')

    if ingdId == None or ingdId == 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    else:
        ingdId = int(ingdId)

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    ingd = JoinedIngredient.objects.order_by('-ingd_id').raw('''
        SELECT 
            ingredient.*,
            categ1.name as category1_name,
            categ2.name as category2_name,
            categ3.name as category3_name,
            categ4.name as category4_name,
            reg_user.username as reg_admin_name, 
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.ingredient
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = ingredient.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = ingredient.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = ingredient.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = ingredient.category4_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = ingredient.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = ingredient.update_admin
        LEFT OUTER JOIN image ON image.content_id = ingredient.ingd_id AND image.content_type = 300 AND image.image_type = 0
        WHERE ingredient.ingd_id = %d
    ''' % ingdId)

    if ingd == None:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    
    serialize_ingd = JoinedIngredientSerializer(ingd[0]) 
    ingd_bjson = JSONRenderer().render(serialize_ingd.data)    
    stream = io.BytesIO(ingd_bjson)
    ingd_dict = JSONParser().parse(stream)    
    ingd_json = json.dumps(ingd_dict, ensure_ascii=False)
    context['ingredient'] = ingd_json

    logger.debug(ingd_json)

    # get images
    images = Image.objects.filter(content_type=ContentInfo.CONTENT_TYPE_INGREDIENT, content_id=ingd[0].ingd_id)   
    serialize_images = ImageSerializer(images, many=True)     
    images_bjson = JSONRenderer().render(serialize_images.data)    
    images_stream = io.BytesIO(images_bjson)
    images_dict = JSONParser().parse(images_stream)    
    images_json = json.dumps(images_dict, ensure_ascii=False)
    context['images'] = images_json

    html_template = loader.get_template( 'modify_ingredient.html' )   
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def modifyEquipment(request):
    
    logger.debug("This is modifyEquipment View ... ")

    context = {}
    context['segment'] = 'modifyEquipment'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'


    # check permission
    # perm = request.user.has_perm('raw_data_manager.modify_equipment')
    # if perm == False:
    #     html_template = loader.get_template( 'page-403.html' )
    #     return HttpResponse(html_template.render(context, request))


    # load data
    equipId = request.GET.get('equipId')

    if equipId == None or equipId == 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    else:
        equipId = int(equipId)

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    equip = JoinedEquipment.objects.order_by('-equip_id').raw('''
        SELECT 
            equipment.*,
            categ1.name as category1_name,
            categ2.name as category2_name,
            categ3.name as category3_name,
            categ4.name as category4_name,
            reg_user.username as reg_admin_name, 
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.equipment
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = equipment.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = equipment.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = equipment.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = equipment.category4_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = equipment.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = equipment.update_admin
        LEFT OUTER JOIN image ON image.content_id = equipment.equip_id AND image.content_type = 400 AND image.image_type = 0
        WHERE equipment.equip_id = %d
    ''' % equipId)

    if equip == None:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    
    serialize_equip = JoinedEquipmentSerializer(equip[0]) 
    equip_bjson = JSONRenderer().render(serialize_equip.data)    
    stream = io.BytesIO(equip_bjson)
    equip_dict = JSONParser().parse(stream)    
    equip_json = json.dumps(equip_dict, ensure_ascii=False)
    context['equipment'] = equip_json

    logger.debug(equip_json)

    # get images
    images = Image.objects.filter(content_type=ContentInfo.CONTENT_TYPE_EQUIP, content_id=equip[0].equip_id)   
    serialize_images = ImageSerializer(images, many=True)     
    images_bjson = JSONRenderer().render(serialize_images.data)    
    images_stream = io.BytesIO(images_bjson)
    images_dict = JSONParser().parse(images_stream)    
    images_json = json.dumps(images_dict, ensure_ascii=False)
    context['images'] = images_json

    html_template = loader.get_template( 'modify_equipment.html' )   
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/admin/login/")
def wordList(request):
    
    context = {}
    context['segment'] = 'list_word'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # load data
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    wordList = JoinedWord.objects.order_by('-word_id').raw('''
        SELECT 
            word.*,
            reg_user.username as reg_admin_name,
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.word
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = word.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = word.update_admin
        LEFT OUTER JOIN image ON image.content_id = word.word_id AND image.content_type = 500 AND image.image_type = 0
        ORDER BY word_id DESC
    ''')

    paginator = Paginator(wordList, perPage)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context['word_list'] = page_obj

    html_template = loader.get_template( 'list_word.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def modifyWord(request):
    
    logger.debug("This is modifyWord View ... ")

    context = {}
    context['segment'] = 'modifyWord'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'


    # check permission
    # perm = request.user.has_perm('raw_data_manager.modify_word')
    # if perm == False:
    #     html_template = loader.get_template( 'page-403.html' )
    #     return HttpResponse(html_template.render(context, request))


    # load data
    wordId = request.GET.get('wordId')

    if wordId == None or wordId == 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    else:
        wordId = int(wordId)

    word = JoinedWord.objects.order_by('-word_id').raw('''
        SELECT 
            word.*,
            reg_user.username as reg_admin_name, 
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.word
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = word.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = word.update_admin
        LEFT OUTER JOIN image ON image.content_id = word.word_id AND image.content_type = 500 AND image.image_type = 0
        WHERE word.word_id = %d
    ''' % wordId)

    if word == None:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    
    serialize_word = JoinedWordSerializer(word[0]) 
    word_bjson = JSONRenderer().render(serialize_word.data)    
    stream = io.BytesIO(word_bjson)
    word_dict = JSONParser().parse(stream)    
    word_json = json.dumps(word_dict, ensure_ascii=False)
    context['word'] = word_json

    logger.debug(word_json)

    # get images
    images = Image.objects.filter(content_type=ContentInfo.CONTENT_TYPE_WORD, content_id=word[0].word_id)   
    serialize_images = ImageSerializer(images, many=True)     
    images_bjson = JSONRenderer().render(serialize_images.data)    
    images_stream = io.BytesIO(images_bjson)
    images_dict = JSONParser().parse(images_stream)    
    images_json = json.dumps(images_dict, ensure_ascii=False)
    context['images'] = images_json

    html_template = loader.get_template( 'modify_word.html' )   
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def cocktailList(request):
    
    context = {}
    context['segment'] = 'list_cocktail'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # load data
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    cocktailList = JoinedCocktail.objects.order_by('-cocktail_id').raw('''
        SELECT 
            cocktail.*,
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

    context['cocktail_list'] = page_obj

    html_template = loader.get_template( 'list_cocktail.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/admin/login/")
def modifyCocktail(request):   

    context = {}
    context['segment'] = 'modifyCocktail'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # check permission
    # perm = request.user.has_perm('raw_data_manager.modify_cocktail')
    # if perm == False:
    #     html_template = loader.get_template( 'page-403.html' )
    #     return HttpResponse(html_template.render(context, request))

    # load data
    cocktailId = request.GET.get('cocktailId')

    if cocktailId == None or cocktailId == 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    else:
        cocktailId = int(cocktailId)

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    cocktail = JoinedCocktail.objects.order_by('-cocktail_id').raw('''
        SELECT 
            cocktail.*,
            reg_user.username as reg_admin_name,
            update_user.username as update_admin_name,
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key
        FROM tipsy_raw.cocktail
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = cocktail.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = cocktail.update_admin
        LEFT OUTER JOIN image ON image.content_id = cocktail.cocktail_id AND image.content_type = 200 AND image.image_type = 0
        WHERE cocktail.cocktail_id = %d
    ''' % cocktailId)

    if cocktail == None:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    
    # set detail_json data
    context['detail_json'] = cocktail[0].detail_json

    # set cocktail data
    cocktail[0].detail_json = ""
    serialize_cocktail = JoinedCocktailSerializer(cocktail[0]) 
    cocktail_bjson = JSONRenderer().render(serialize_cocktail.data)    
    stream = io.BytesIO(cocktail_bjson)
    cocktail_dict = JSONParser().parse(stream)    
    cocktail_json = json.dumps(cocktail_dict, ensure_ascii=False)
    context['cocktail'] = cocktail_json

    # set cocktail images
    images = Image.objects.filter(content_type=ContentInfo.CONTENT_TYPE_COCTAIL, content_id=cocktail[0].cocktail_id)   
    serialize_images = ImageSerializer(images, many=True)     
    images_bjson = JSONRenderer().render(serialize_images.data)    
    images_stream = io.BytesIO(images_bjson)
    images_dict = JSONParser().parse(images_stream)    
    images_json = json.dumps(images_dict, ensure_ascii=False)
    context['images'] = images_json

    html_template = loader.get_template( 'modify_cocktail.html' )   
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def crawledLiquorImageList(request):
    context = {}
    context['segment'] = 'crawled_data_mng/list_crawled_liquor_image'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # load data
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('perPage', 10))
    offset = (page - 1) * per_page

    liquor_list = GroupedCrawledLiquorImage.objects.order_by('-liquor_id').raw('''
        	SELECT 
                cli.id
                , cli.liquor_id
                , liquor.name_kr
                , liquor.name_en
                , count(liquor.liquor_id) total_cnt
                , SUM(cli.is_use = 0) AS usable
                , SUM(cli.is_use = 1) AS unusable
                , SUM(cli.is_use = 2) AS waiting
            FROM  crawled_liquor_image cli
            INNER JOIN raw_liquor liquor on cli.liquor_id = liquor.liquor_id
            GROUP BY cli.liquor_id
    ''')

    paginator = Paginator(liquor_list, per_page)
    page_obj = paginator.get_page(page)

    context['liquor_list'] = page_obj

    html_template = loader.get_template( 'crawled_data_mng/list_crawled_liquor_image.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/admin/login/")
def crawledLiquorImageDetail(request):
    context = {}
    context['segment'] = 'crawled_data_mng/detail_crawled_liquor_image'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    # TODO: select liquor info
    liquor_id = int(request.GET.get('liquorId', 0))
    
    if liquor_id == 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))
    
    #liquor = RawLiquor.objects.get(liquor_id=liquor_id)
    liquor_qset = JoinedLiquor.objects.raw("" +
        '''SELECT 
            raw_liquor.*, 
            categ1.name as category1_name, 
            categ2.name as category2_name, 
            categ3.name as category3_name, 
            categ4.name as category4_name, 
            country.name as country_name, 
            reg_user.username as reg_admin_name, 
            update_user.username as update_admin_name, 
            if(image.s3_key is null, 'image/liquor/default_image.png', image.s3_key) as s3_key 
        FROM tipsy_raw.raw_liquor 
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = raw_liquor.category1_id 
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = raw_liquor.category2_id 
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = raw_liquor.category3_id 
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = raw_liquor.category4_id 
        LEFT OUTER JOIN tipsy_raw.country ON country.country_id = raw_liquor.country_id 
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = raw_liquor.reg_admin 
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = raw_liquor.update_admin 
        LEFT OUTER JOIN image ON image.content_id = raw_liquor.liquor_id AND image.content_type = 100 AND image.image_type = 0 
        WHERE raw_liquor.liquor_id = %s''' % (liquor_id))

    if len(liquor_qset) <= 0:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    print(liquor_qset[0])

    context['liquor'] = liquor_qset[0]

    html_template = loader.get_template( 'crawled_data_mng/detail_crawled_liquor_image.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def recommandTest(request):
    
    context = {}
    context['segment'] = 'test_recommand'
    context['prefix'] = 'http://tipsy.co.kr/admin'
    context['imgprefix'] = 'https://tipsy-pro.s3.ap-northeast-2.amazonaws.com'

    html_template = loader.get_template( 'test/recommand.html' )
    return HttpResponse(html_template.render(context, request))