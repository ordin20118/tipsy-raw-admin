# -*- encoding: utf-8 -*-
from django.urls import path, re_path
from raw_data_manager import view
from raw_data_manager import view_dashboard
from raw_data_manager.views.rembg import rembg
from raw_data_manager.views.ai_view import ana_description_with_chatgpt
from raw_data_manager.views import liquor_article_queue_view

urlpatterns = [

    path('api/categ_tree', view.categ_tree, name='categTree'),
    path('api/country', view.country, name='country'),
    path('api/liquor', view.liquor, name='liquor'),
    path('api/cocktail', view.cocktail, name='cocktail'),
    path('api/ingredient', view.ingredient, name='ingredient'),
    path('api/equipment', view.equipment, name='equipment'),
    path('api/word', view.word, name='word'),
    path('api/image', view.image, name='image'),
    path('api/page_info/<str:name>', view.page_info, name='pageInfo'),
    path('api/liquor_dup_chck', view.liquor_dup_chck, name='liquorDupChck'),
    path('api/ingredient_dup_chck', view.ingredient_dup_chck, name='ingredientDupChck'),
    path('api/equipment_dup_chck', view.equipment_dup_chck, name='equipmentDupChck'),
    path('api/word_dup_chck', view.word_dup_chck, name='wordDupChck'),
    path('api/cocktail_dup_chck', view.cocktail_dup_chck, name='cocktailDupChck'),
    path('api/search', view.search, name='search'),
    path('api/ocr', view.ocr, name='ocr'),
    path('api/recommand/liquor', view.recommand, name='recommand'),

    path('api/liquor/crawled/image', view.crawled_liquor_image, name='crawled_liquor_image'),
    path('api/liquor/crawled/image_list', view.crawled_liquor_image_list, name='crawled_liquor_image_list'),

    path('api/liquor/article-queue', liquor_article_queue_view.create_queue, name='createLiquorArticleQueue'),

    path('api/dashboard/timeline/new', view_dashboard.newContentTimeline, name='newTimeline'),
    path('api/dashboard/timeline/managelog', view_dashboard.manageTimeline, name='manageTimeline'),    
    path('api/dashboard/stats/crawled', view_dashboard.crawledDataStats, name='crawledDataStats'),    
    path('api/dashboard/stats/liquor', view_dashboard.liquorDataStats, name='liquorDataStats'),    

    path('api/rembg_queue', rembg, name='rembg'),
    path('api/openai/ana_desc', ana_description_with_chatgpt, name='ana_description_with_chatgpt'),

    path('permission/create_permissions', view.createPermissions, name='createPermissions'),    
    
    

    re_path(r'^image/.*\.*', view.image, name='image'),

]
