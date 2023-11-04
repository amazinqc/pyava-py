from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST, require_safe

from back.models import Server, Tool, TypeChoice
from pyava.agent import HttpAgent

from .json import Error, Json, json_request, json_response

# Create your views here.


@require_safe
@json_response
def options(_: WSGIRequest, option_id=None):
    choices = TypeChoice.objects.filter(type__gt=0)
    if option_id is None:
        return Json(choices)
    return Json(choices.filter(option=option_id))


@require_safe
@json_response
def codes(_: WSGIRequest, type_id=None):
    if type_id is None:
        return Json(Tool.objects.filter(id__gt=0))
    return Json(Tool.objects.filter(type=type_id))


@require_safe
@json_response
def servers(_: WSGIRequest):
    return Json(Server.objects.all())


@require_safe
@json_response
def hints(_: WSGIRequest):
    return Json({key: type(val).__name__ for key, val in Tool.codenv().items()})


class CodeView(View):

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
        kwargs = {}
        for arg in args:
            name = arg['name']
            if name in raw_args:
                kwargs[name] = raw_args[name]
            elif 'default' not in arg:
                return Error(f'缺少参数<{name}>')
            else:
                pass
        with HttpAgent(server.agent_url):
            return Json(tool.code(**kwargs))


@require_POST
@json_request
def debug(draft: dict):
    if 'code' not in draft:
        return Error("未识别的格式")
    raw_code = draft["code"]
    raw_args = draft.get('args', {})
    sid = draft.get('sid')

    class DebugAgent(HttpAgent):

        def __init__(self, agent: bool = False) -> None:
            if agent:
                super().__init__('http://127.0.0.1:8080/Local')
            self.agent = agent

        def debug(self, data) -> dict:
            return super().debug(data) if self.agent else {'code': 200, 'data': data}

    if sid and (server := Server.objects.filter(pk=sid).first()):
        agent = HttpAgent(server.agent_url)
    else:
        agent = DebugAgent(True)
    with agent:
        tool = Tool(cmd=raw_code)
        args = tool.args()
        kwargs = {}
        for arg in args:
            name = arg['name']
            if name in raw_args:
                kwargs[name] = raw_args[name]
            elif 'default' not in arg:
                return Error(f'缺少参数<{name}>')
            else:
                pass
        return Json(tool.code(**kwargs))
