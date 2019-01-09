# Create your tasks here
from __future__ import absolute_import, unicode_literals
import XProject.celery as cc
import redis
import XProject.settings as settings
import json

app = cc.app
# redis 连接池
pool = redis.ConnectionPool(host="192.168.1.30", db=6)


class StepsStatus:
    """
    任务状态机
                 *--->stopped---------------->starting---->running---->stopping-->stopped
                        |----<---error---<-------|           |                      |
                        |           |----------<-------------|                      |
                        |-----------------------------------------------------------|
    """
    def __init__(self, **kwargs):
        self.path = None
        self.command_timestamp = None
        self.status = 'stopped'
        self.last_error = ''

        for key, value in kwargs.items():
            setattr(self, key, value)

    def pull(self):
        r = redis.Redis(connection_pool=pool)
        status_bytes = r.get(settings.redis_global_config['工步执行状态'])
        try:
            status = json.loads(status_bytes)
        except:
            return vars(self)

        for key in vars(self):
            setattr(self, key, status[key])

        return vars(self)

    def push(self):
        status = json.dumps(vars(self), ensure_ascii=False)
        r = redis.Redis(connection_pool=pool)
        r.set(settings.redis_global_config['工步执行状态'], status)
        return vars(self)


@app.task
def start_step(steps_path):
    """
    启动工步
    :param steps_path:
    :return:
    """
    r = redis.Redis(connection_pool=pool)
    steps = r.get(steps_path)

    if steps is None:
        status = StepsStatus(status="error", last_error="工步程序未就绪")
        return status.push()
    else:
        status = StepsStatus(path=steps_path, status="starting", last_error='')
        return status.push()


@app.task
def steps_status():
    """
    获取当前工步状态
    :return:
    """
    status = StepsStatus()
    return status.pull()


@app.task
def stop_step():
    """
    停止工步
    :return:
    """
    status = StepsStatus(status="stopped", last_error='')

    return status.push()

