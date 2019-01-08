# -*- coding: UTF-8 -*-
__author__ = 'lijie'
__version__ = "1.0"

from django.http import *
from django.urls import path
import X.steps as steps
import X.api as api


urlpatterns = [
    path('', api.response_not_implement),
    path('basic/', api.response_not_implement),
    path('open/', api.response_not_implement),
    path('newline/', api.response_not_implement),
    path('newline/<str:func>/set/<value>/', api.response_not_implement),
    path('bms/', api.response_not_implement),
    path('step/', steps.urls),
]


urls = (urlpatterns, "v1.0", "api")
