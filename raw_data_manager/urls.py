# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from raw_data_manager import views

urlpatterns = [

    # The home page
    path('api/categ_tree', views.categTree, name='categTree'),

]
