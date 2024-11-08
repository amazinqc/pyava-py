from abc import abstractmethod
from functools import wraps
from typing import Iterable, Any

from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.http import JsonResponse

from pyava.agent import AgentError


class Jsonify():

    @abstractmethod
    def json(self) -> dict:
        pass


def Json(data: Jsonify | dict | QuerySet):
    return JsonResponse({'code': 200, 'data': jsonify(data), })


def Error(msg: str | Any):
    return JsonResponse({'code': 500, 'message': msg})


def jsonify(data: Any):
    if isinstance(data, Jsonify):
        return data.json()
    if isinstance(data, dict):
        return data
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        return [jsonify(d) for d in data]
    return data


def json_request(view):
    from json import decoder, loads

    @json_response
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            args = [loads(arg.body) if isinstance(
                arg, WSGIRequest) else arg for arg in args]
        except decoder.JSONDecodeError:
            return Error('JSON解析错误')
        return view(*args, **kwargs)
    return wrapper


def json_response(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except AgentError as ae:
            return Error(ae.args[0] if ae.args else str(e))
        except BaseException as e:
            import logging
            logging.getLogger('back').error('执行异常', exc_info=e)
            return Error(str(e))
    return wrapper
