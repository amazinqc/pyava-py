from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_safe, require_POST
from back.models import Tool

from .json import Json, Error

from pytool import variables

# Create your views here.


@require_safe
def index(request):
    return HttpResponse('Hello, world')


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
def exec(request):
    import json
    return Json(json.loads(request.body))
