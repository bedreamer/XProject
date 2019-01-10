# -*- coding: UTF-8 -*-
__author__ = 'lijie'
__version__ = "1.0"

from django.http import *
from django.urls import path
import X.steps as steps
import X.api as api
import redis
import json
import XProject.settings as setttings
import X.tasks as tasks


def be_evaluate(r):
    evaluate = {
        "SN": "@",
        "激活状态": "待激活",
        "用户": "@",
        "过期日期": "@"
    }
    r.hset(setttings.redis_global_config['基本信息哈希表'], "license", json.dumps(evaluate, ensure_ascii=False))


def get_basic_information(request):
    """
    获取系统的基本信息
    :param request:
    :return:
    """
    basic_list = ["bms", "newline", "step", "license", "entry"]
    r = redis.Redis(connection_pool=api.pool)

    basic_bms = r.hget(setttings.redis_global_config['基本信息哈希表'], "bms")
    basic_newline = r.hget(setttings.redis_global_config['基本信息哈希表'], "newline")
    basic_step = r.hget(setttings.redis_global_config['基本信息哈希表'], "step")
    be_evaluate(r)

    basic_license = r.hget(setttings.redis_global_config['基本信息哈希表'], "license")
    basic_entry = r.hget(setttings.redis_global_config['基本信息哈希表'], "entry")

    if None in [basic_bms, basic_newline, basic_step, basic_license, basic_entry]:
        return api.response_error(request, reason="基本数据还未准备好")

    data = {
        "bms": json.loads(basic_bms),
        "newline": json.loads(basic_newline),
        "step": json.loads(basic_step),
        "license": json.loads(basic_license),
        "entry": basic_entry.decode()
    }

    return api.response_ok(request, data=data)


def get_open_device(request):
    """
    打开设备
    :param request:
    :return:
    """
    status = tasks.open_device.delay().get()
    return api.response_ok(request, data=status)


def get_close_device(request):
    """
    关闭设备
    :param request:
    :return:
    """
    status = tasks.close_device.delay().get()
    return api.response_ok(request, data=status)


def get_newline_information(request):
    """
    获取恒温恒流设备的基本信息
    :param request:
    :return:
    """
    return api.response_not_implement(request)


def get_set_newline_parameters(request, func, value):
    """
    设置恒温恒流的参数
    :param request:
    :param func:
    :param value:
    :return:
    """
    return api.response_not_implement(request)


def get_bms_information(request):
    """
    获取BMS的信息
    :param request:
    :return:
    """
    return api.response_not_implement(request)


urlpatterns = [
    path('', api.response_not_implement),
    path('basic/', get_basic_information),
    path('open/', get_open_device),
    path('close/', get_close_device),
    path('newline/', api.response_not_implement),
    path('newline/<str:func>/set/<value>/', api.response_not_implement),
    path('bms/', api.response_not_implement),
    path('step/', steps.urls),
]


urls = (urlpatterns, "v1.0", "api")
