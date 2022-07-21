# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('liquor_list.html', views.liquorList, name='liquorList'),
    path('cocktail_list.html', views.cocktailList, name='cocktailList'),
    path('ingredient_list.html', views.ingredientList, name='ingredientList'),
    path('equipment_list.html', views.equipmentList, name='equipmentList'),
    path('modify_liquor.html', views.modifyLiquor, name='modifyLiquor'),
    path('modify_cocktail.html', views.modifyCocktail, name='modifyCocktail'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

    
    

]
