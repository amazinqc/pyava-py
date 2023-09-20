from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST, require_safe

import pytool
from back.models import Server, Tool, TypeChoice

from .json import Error, Json, json_request, json_response
from .utils import codenv

# Create your views here.


@require_safe
@json_response
def options(_: WSGIRequest):
    return Json(TypeChoice.objects.all())


@require_safe
@json_response
def tools(_: WSGIRequest):
    return Json(Tool.objects.all())


@require_safe
@json_response
def servers(_: WSGIRequest):
    return Json(Server.objects.all())


@require_safe
@json_response
def hints(_: WSGIRequest):
    return Json({key: type(val).__name__ for key, val in codenv().items()})


class CodeView(View):
    AGENT_PATH = 'LocalTest'

    @json_response
    def get(self, _: WSGIRequest, id):
        tool = Tool.objects.filter(pk=id).first()
        if tool is None:
            return Error("指令代码不存在")
        return Json(tool)

    @json_request
    def post(self, raw_params: dict, id: int):
        tool = Tool.objects.filter(pk=id).first()
        if tool is None:
            return Error("指令代码不存在")
        sid = raw_params.get('sid')
        if not sid:
            return Error('请选择服务器')
        if not (server := Server.objects.filter(pk=sid).first()):
            return Error('服务器不存在')

        raw_args = raw_params.get('args', {})
        args = tool.args()
        for arg in args:
            name = arg['name']
            if 'default' not in arg and name not in raw_args:
                return Error(f'缺少参数<{name}>')
        with pytool.JavaAgent(f'http://{server.host}:{server.port}/{self.AGENT_PATH}'):
            return Json(tool.code(**raw_args))


@require_POST
@json_request
def debug(draft: dict):
    if 'code' not in draft:
        return Error("未识别的格式")
    raw_code = draft["code"]
    raw_args = draft.get('args', {})

    class DebugAgent(pytool.JavaAgent):

        def __init__(self) -> None:
            pass

        def debug(self, **kvargs) -> dict:
            return {'code': 200, 'data': kvargs}

    with DebugAgent():
        try:
            tool = Tool(cmd=raw_code)
            args = tool.args()
            for arg in args:
                name = arg['name']
                if 'default' not in arg and name not in raw_args:
                    return Error(f'缺少参数<{name}>')
            return Json(tool.code(**raw_args))
        except BaseException as e:
            import logging
            logging.getLogger('back').error(draft, exc_info=e)
            return Error(str(e))
