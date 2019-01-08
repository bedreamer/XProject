# -*- coding: UTF-8 -*-
__author__ = 'lijie'
from django.http import *
import time
import redis


# REDIS 连接池
pool = redis.ConnectionPool(host='127.0.0.1', db=5)
redis_global_config = {
    "工步状态": "steps:status",
    "支持的判定条件": "steps:supported_conditions",
    "工步存储文件名": "steps:file_path",
    "工步逻辑代码": "steps:logic_code",
}


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
