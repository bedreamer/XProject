# -*- coding: UTF-8 -*-
__author__ = 'lijie'
from django.http import *
from django.urls import path
import X.api as api
import redis
import json


def get_supported_conditions(request):
    """
    返回支持的比较条件列表
    :return:
    """
    try:
        query = redis.Redis(connection_pool=api.pool)
    except Exception as e:
        return api.response_redis_error(request, detail=str(e))

    conditions = query.get(api.redis_global_config['支持的判定条件'])
    if conditions is None:
        return api.response_backend_error(request, detail="后端服务未准备好数据.")

    try:
        data = json.loads(conditions)
    except Exception as e:
        return api.response_redis_error(request, detail="后端数据格式错误("+str(e)+')')

    return api.response_ok(request, data=data)


def post_save_single_step(request, step_name):
    """
    保存单个工步
    :param request: 请求
    :param step_name: 工步名
    :return: 全部工步列表
    """
    try:
        query = redis.Redis(connection_pool=api.pool)
    except Exception as e:
        return api.response_redis_error(request, detail=str(e))

    try:
        step = json.loads(request.body)
    except Exception as e:
        return api.response_error(request, "提交的数据格式错误("+str(e)+')')

    logic_step = query.get(api.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        logic_step = "{}"

    logic_json = json.loads(logic_step)
    new_logic_code = dict(logic_json, **{step_name:step})

    query.set(api.redis_global_config['工步逻辑代码'], json.dumps(new_logic_code, ensure_ascii=False))

    data = {
        "main": "step1",
        "steps": new_logic_code
    }

    return api.response_ok(request, data=data)


def get_delete_single_step(request, step_name):
    """
    删除单个工步
    :param request: 请求
    :param step_name: 工步名
    :return: 全部工步列表
    """
    try:
        query = redis.Redis(connection_pool=api.pool)
    except Exception as e:
        return api.response_redis_error(request, detail=str(e))

    logic_step = query.get(api.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        data = {"main": None, "steps": {}}
        return api.response_ok(request, data=data)

    json_step = json.loads(logic_step)
    try:
        del json_step[step_name]
        query.set(api.redis_global_config['工步逻辑代码'], json.dumps(json_step, ensure_ascii=False))
    except Exception as e:
        pass

    data = {
        "main": "step1",
        "steps": json_step
    }

    return api.response_ok(request, data=data)


def get_fetch_single_step(request, step_name):
    """
    获取单个工步对象
    :param request: 请求
    :param step_name: 工步名
    :return: 单个公布对象
    """
    try:
        query = redis.Redis(connection_pool=api.pool)
    except Exception as e:
        return api.response_redis_error(request, detail=str(e))

    logic_step = query.get(api.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        data = {"main": None, "steps": {}}
        return api.response_ok(request, data=data)

    json_step = json.loads(logic_step)
    try:
        obj = json_step[step_name]
    except Exception as e:
        return api.response_error(request, reason="无法获取指定工步名("+str(e)+')')

    return api.response_ok(request, data=obj)


urlpatterns = [
    # GET 获取全部工步的判定条件
    path('supported_conditions/', get_supported_conditions),
    # POST 保存单个工步
    path('<str:step_name>/save/', post_save_single_step),
    # GET 删除单个工步
    path('<str:step_name>/delete/', get_delete_single_step),
    # GET 获取单个工步内容
    path('<str:step_name>/get/', get_fetch_single_step),
    path('check/', api.response_not_implement),
    path('start/', api.response_not_implement),
    path('stop/', api.response_not_implement),
]

urls = (urlpatterns, "steps", "steps")
