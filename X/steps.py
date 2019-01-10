# -*- coding: UTF-8 -*-
__author__ = 'lijie'
from django.http import *
from django.urls import path
import X.api as api
import redis
import json
import X.tasks as tasks
import XProject.settings as settings


def get_supported_conditions(request):
    """
    返回支持的比较条件列表
    :return:
    """
    try:
        query = redis.Redis(connection_pool=api.pool)
    except Exception as e:
        return api.response_redis_error(request, detail=str(e))

    bms_conditions = query.hget(settings.redis_global_config['支持的判定条件'], "bms")
    if bms_conditions is None:
        return api.response_backend_error(request, detail="bms后端服务未准备好数据.")

    newline_conditions = query.hget(settings.redis_global_config['支持的判定条件'], "newline")
    if newline_conditions is None:
        return api.response_backend_error(request, detail="newline后端服务未准备好数据.")

    step_conditions = query.hget(settings.redis_global_config['支持的判定条件'], "step")
    if step_conditions is None:
        return api.response_backend_error(request, detail="step后端服务未准备好数据.")

    try:
        bms_data = json.loads(bms_conditions)
        newline_data = json.loads(newline_conditions)
        step_data = json.loads(step_conditions)
        data = dict(bms_data, **dict(newline_data, **step_data))
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

    logic_step = query.get(settings.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        logic_step = "{}"

    logic_json = json.loads(logic_step)
    new_logic_code = dict(logic_json, **{step_name:step})

    query.set(settings.redis_global_config['工步逻辑代码'], json.dumps(new_logic_code, ensure_ascii=False))

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

    logic_step = query.get(settings.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        data = {"main": None, "steps": {}}
        return api.response_ok(request, data=data)

    json_step = json.loads(logic_step)
    try:
        del json_step[step_name]
        query.set(settings.redis_global_config['工步逻辑代码'], json.dumps(json_step, ensure_ascii=False))
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

    logic_step = query.get(settings.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        return api.response_error(request, reason="无法获取指定工步名，服务未就绪")

    json_step = json.loads(logic_step)
    try:
        obj = json_step[step_name]
    except Exception as e:
        return api.response_error(request, reason="无法获取指定工步名("+str(e)+')')

    return api.response_ok(request, data=obj)


def get_check_steps(request):
    """
    对已有的工步进行语法检查
    :param request: 请求
    :return: 成功返回全部工步
    """
    try:
        query = redis.Redis(connection_pool=api.pool)
    except Exception as e:
        return api.response_redis_error(request, detail=str(e))

    logic_step = query.get(settings.redis_global_config['工步逻辑代码'])
    if logic_step is None:
        return api.response_error(request, reason="无法获取指定工步名，服务未就绪")

    steps = json.loads(logic_step)
    for name, step in steps.items():
        if step['true'] != '$auto' and step['true'] not in steps:
            return api.response_error(request,
                                      reason="".join(["工步=", name, "的 `匹配` 跳转目标:", step['true'], "不存在"]))

        if step['false'] != '$auto' and step['false'] not in steps:
            return api.response_error(request,
                                      reason="".join(["工步=", name, "的 `不匹配` 跳转目标:", step['false'], "不存在"]))

        if len(step['tiaojian']) not in {3, 7}:
            return api.response_error(request, reason="".join(["工步=", name, "的判定条件个数错误!"]))

    data = {
        "main": "step1",
        "steps": steps
    }

    return api.response_ok(request, data=data)


def get_start_step(request):
    """
    启动工步
    :param request: 请求
    :return: 成功返回...
    """
    result = tasks.start_step.delay(settings.redis_global_config['工步逻辑代码'])
    return api.response_ok(request, data=result.get())


def get_stop_step(request):
    """
    停止工步
    :param request: 请求
    :return:
    """
    result = tasks.stop_step.delay()
    return api.response_ok(request, data=result.get())


def get_fetch_step_status(request):
    """
    获取工步状态
    :param request: 请求
    :return: 工步状态
    """
    result = tasks.steps_status.delay()
    return api.response_ok(request, data=result.get())


urlpatterns = [
    # GET 获取全部工步的判定条件
    path('supported_conditions/', get_supported_conditions),
    # POST 保存单个工步
    path('<str:step_name>/save/', post_save_single_step),
    # GET 删除单个工步
    path('<str:step_name>/delete/', get_delete_single_step),
    # GET 获取单个工步内容
    path('<str:step_name>/get/', get_fetch_single_step),
    # GET 检查已有的工步
    path('check/', get_check_steps),
    # GET 启动工步
    path('start/', get_start_step),
    # GET 停止工步
    path('stop/', get_stop_step),
    # GET 当前工步运行状态
    path('status/', get_fetch_step_status),
]

urls = (urlpatterns, "steps", "steps")
