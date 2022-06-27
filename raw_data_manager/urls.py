# -*- encoding: utf-8 -*-
from django.urls import path, re_path
from raw_data_manager import views

urlpatterns = [

    path('api/categ_tree', views.categ_tree, name='categTree'),
    path('api/country', views.country, name='country'),
    path('api/liquor', views.liquor, name='liquor'),
    path('api/cocktail', views.cocktail, name='cocktail'),
    path('api/ingredient', views.ingredient, name='ingredient'),
    path('api/equipment', views.equipment, name='equipment'),
    path('api/image', views.image, name='image'),
    path('api/page_info/<str:name>', views.page_info, name='pageInfo'),
    path('api/liquor_dup_chck', views.liquor_dup_chck, name='liquorDupChck'),
    path('api/ingredient_dup_chck', views.ingredient_dup_chck, name='ingredientDupChck'),
    path('api/equipment_dup_chck', views.equipment_dup_chck, name='equipmentDupChck'),
    path('api/cocktail_dup_chck', views.cocktail_dup_chck, name='cocktailDupChck'),
    path('api/search', views.search, name='search'),
    #path('api/dashboard/count', views.dashboardCount, name='dashboardCount'),
    re_path(r'^image/.*\.*', views.image, name='image'),

]
