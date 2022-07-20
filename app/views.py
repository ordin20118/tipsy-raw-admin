# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.core.paginator import Paginator

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

import io
import json

from raw_data_manager.forms import *
from raw_data_manager.models import *
from raw_data_manager.serializers import *

@login_required(login_url="/admin/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'
    # context['prefix'] = 'http://211.37.150.105:8000'
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

#@login_required(login_url="/login/")
def pages(request):

    context = {}
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'
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
    context['segment'] = 'liquorList'
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'

    # load data
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))

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

    context['liquor_list'] = page_obj

    html_template = loader.get_template( 'liquor_list.html' )
    return HttpResponse(html_template.render(context, request))




@login_required(login_url="/admin/login/")
def liquorModify(request):
    
    print("This is liquorModify View ... ")

    context = {}
    context['segment'] = 'liquorModify'
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'

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
    context['segment'] = 'ingredientList'
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'

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
            if(image.path is null, 'default', image.path) as rep_img
        FROM tipsy_raw.ingredient
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = ingredient.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = ingredient.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = ingredient.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = ingredient.category4_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = ingredient.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = ingredient.update_admin
        LEFT OUTER JOIN image ON image.content_id = ingredient.ingd_id AND image.content_type = 300 AND image.image_type = 0
    ''')

    paginator = Paginator(ingredientList, perPage)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context['ingredient_list'] = page_obj

    html_template = loader.get_template( 'ingredient_list.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/admin/login/")
def equipmentList(request):
    
    context = {}
    context['segment'] = 'equipList'
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'

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
            if(image.path is null, 'default', image.path) as rep_img
        FROM tipsy_raw.equipment
        LEFT OUTER JOIN tipsy_raw.raw_category categ1 ON categ1.id = equipment.category1_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ2 ON categ2.id = equipment.category2_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ3 ON categ3.id = equipment.category3_id
        LEFT OUTER JOIN tipsy_raw.raw_category categ4 ON categ4.id = equipment.category4_id
        LEFT OUTER JOIN tipsy_raw.auth_user reg_user ON reg_user.id = equipment.reg_admin
        LEFT OUTER JOIN tipsy_raw.auth_user update_user ON update_user.id = equipment.update_admin
        LEFT OUTER JOIN image ON image.content_id = equipment.equip_id AND image.content_type = 400 AND image.image_type = 0
    ''')

    paginator = Paginator(equipmentList, perPage)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context['equipment_list'] = page_obj

    html_template = loader.get_template( 'equipment_list.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/admin/login/")
def cocktailList(request):
    
    context = {}
    context['segment'] = 'cocktailList'
    context['prefix'] = 'http://tipsy.co.kr:8000/admin'
    context['imgprefix'] = 'http://tipsy.co.kr:8000/admin/raw_data_manager/image'

    # load data
    page = int(request.GET.get('page', 1))
    perPage = int(request.GET.get('perPage', 10))

    # TODO: join에 대한 내용을 model에 반영해서 조회하기
    cocktailList = JoinedCocktail.objects.order_by('-cocktail_id').raw('''
        SELECT 
            cocktail.*,
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

    context['cocktail_list'] = page_obj

    html_template = loader.get_template( 'cocktail_list.html' )
    return HttpResponse(html_template.render(context, request))