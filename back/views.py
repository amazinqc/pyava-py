from django.shortcuts import render
from django.views.decorators.http import require_safe, require_POST
from back.models import Tool

from .json import Json, Error

from pytool import variables

# Create your views here.



@require_safe
def tools(request):
    return Json(Tool.objects.all())


@require_safe
def tips(request):
    return Json(variables())


@require_safe
def code(request, id):
    tool = Tool.objects.filter(pk=id).first()
    if tool is None:
        return Error("指令代码不存在")
    return Json(tool)


@require_POST
def debug(request):
    import json
    draft: dict = json.loads(request.body)
    if 'code' not in draft:
        return Error("未识别的格式")
    raw_code = f'from pytool import *\n{draft["code"]}'
    from pytool import JavaAgent
    import time

    class DebugAgent(JavaAgent):

        def __init__(self) -> None:
            pass

        def debug(self, **kvargs) -> dict:
            return {'code': 200, 'data': kvargs}

    with DebugAgent():
        try:
            exec(raw_code, envs := {})
            if not callable(code := envs.get('code', None)):
                return Error("未识别的代码")
            return Json(code()) # todo parameters
        except BaseException as e:
            import logging
            logging.getLogger('back').error(draft, exc_info=e)
            return Error(str(e))
