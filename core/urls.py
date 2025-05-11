# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from django.conf.urls.static import static
from core.settings import IMAGE_PATH, DATA_ROOT

urlpatterns = [
    path('admins/', admin.site.urls),            # Django admin route
    path("raw_data_manager/", include("raw_data_manager.urls")), # Raw Data Manager API
    path("", include("authentication.urls")),   # Auth routes - login / register
    path("", include("app.urls")),              # UI Kits Html files
]

#urlpatterns += static(MEDIA_URL, document_root=DATA_ROOT)
