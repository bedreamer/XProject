# -*- coding: UTF-8 -*-
__author__ = 'lijie'
from django.http import *
import time
import redis
import platform

if platform.system().lower() == 'windows':
    host = "192.168.1.30"
else:
    host = "127.0.0.1"


# REDIS 连接池
pool = redis.ConnectionPool(host=host, db=6)


def response_error(request, reason, **kwargs):
    """
    返回错误应答
    :param reason: 原因
    :param kwargs: 参数
    :return:
    """
    not_implement_error = dict({
        "status": "error",
        "reason": reason,
        "tsp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }, **kwargs)

    return JsonResponse(not_implement_error, json_dumps_params={"ensure_ascii": False})


def response_ok(request, **kwargs):
    """
    返回正常应答
    :param kwargs: 参数
    :return:
    """
    data = dict({
        "status": "ok",
        "reason": "",
        "tsp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }, **kwargs)

    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


def response_not_implement(request, **kwargs):
    """
    返回未实现的错误应答
    :param kwargs: 参数
    :return:
    """
    return response_error(request, "not implement.", **kwargs)


def response_redis_error(request, **kwargs):
    """
    返回REDIS产生的错误应答
    :param request: 请求
    :param kwargs: 参数
    :return:
    """
    return response_error(request, "redis error.", **kwargs)


def response_backend_error(request, **kwargs):
    """
    返回服务器错误应答
    :param request: 请求
    :param kwargs: 参数
    :return:
    """
    return response_error(request, "backend server error.", **kwargs)
