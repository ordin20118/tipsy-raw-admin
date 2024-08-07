# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [


    # The home page
    path('', views.index, name='home'),
    path('list_liquor.html', views.liquorList, name='liquorList'),
    path('list_cocktail.html', views.cocktailList, name='cocktailList'),
    path('list_ingredient.html', views.ingredientList, name='ingredientList'),
    path('list_equipment.html', views.equipmentList, name='equipmentList'),
    path('list_word.html', views.wordList, name='wordList'),
    path('modify_liquor.html', views.modifyLiquor, name='modifyLiquor'),
    path('modify_cocktail.html', views.modifyCocktail, name='modifyCocktail'),
    path('modify_ingredient.html', views.modifyIngredient, name='modifyIngredient'),
    path('modify_equipment.html', views.modifyEquipment, name='modifyEquipment'),
    path('modify_word.html', views.modifyWord, name='modifyWord'),

    path('crawled_data_mng/list_crawled_liquor_image.html', views.crawledLiquorImageList, name='crawledLiquorImageList'),
    path('crawled_data_mng/detail_crawled_liquor_image.html', views.crawledLiquorImageDetail, name='crawledLiquorImageDetail'),
    path('crawled_data_mng/list_crawled_liquor.html', views.crawled_liquor_list, name='crawled_liquor_list'),
    path('crawled_data_mng/modify_crawled_liquor.html', views.modify_crawled_liquor, name='modify_crawled_liquor'),


    path('test/recommand.html', views.recommandTest, name='recommandTest'),
    

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
