# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
__author__ = 'lijie'

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'XProject.settings')

app = Celery('XProject',
             broker="redis://192.168.1.30:6379/5",
             backend="redis://192.168.1.30:6379/5"
             )

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
