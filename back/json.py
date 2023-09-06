from typing import Iterable
from django.http import JsonResponse

from abc import abstractmethod


class Jsonify():

    @abstractmethod
    def json(self) -> dict:
        pass


def Json(data: Jsonify | dict):
    return JsonResponse({'code': 200, 'data': jsonify(data), })


def Error(msg: str):
    return JsonResponse({'code': 500, 'message': msg})


def jsonify(data: any):
    if isinstance(data, Jsonify):
        return data.json()
    if isinstance(data, dict):
        return data
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        return [jsonify(d) for d in data]
    return data
