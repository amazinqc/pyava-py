from functools import wraps
from typing import Any, Callable, List

from django.core.cache import cache as memory
from django.db import models
from django.db.models import signals
from django.dispatch import receiver

import pyava


def basenv():
    return {key: getattr(pyava, key) for key in pyava.__all__}


def cached[R](compute_func: Callable[[Any], R]) -> Callable[[Any], R]:
    '''
    函数计算属性缓存，一般用于无参函数或者Model成员计算属性
    '''
    @wraps(compute_func)
    def wrapper(*args, **kwargs) -> R:
        if args and isinstance(model := args[0], models.Model):
            if model.pk:
                key = compute_func.__qualname__ + ':' + _get_model_key(model)
            else:
                return compute_func(*args, **kwargs)
        else:
            key = compute_func.__qualname__
        return memory.get_or_set(key, lambda: compute_func(*args, **kwargs))
    return wrapper


def _get_model_key(obj: models.Model) -> str:
    pk = obj.pk
    if isinstance(pk, (list, tuple)):
        key = ':'.join([key, *map(str, pk)])
    else:
        key = str(pk)
    return key


def cachewith(model: models.Model | str, signal: signals.ModelSignal | List[signals.ModelSignal] = ()):
    '''
    绑定Model行为的函数计算缓存
    '''
    def decorator[R](compute_func: Callable[[Any], R]) -> Callable[[Any], R]:

        @receiver(signal=signal, sender=model)
        def remove(instance: models.Model, **kwargs):
            if isinstance(instance, models.Model) and instance.pk:
                key = compute_func.__qualname__ + \
                    ':' + _get_model_key(instance)
            else:
                key = compute_func.__qualname__
            return memory.delete(key)

        return cached(compute_func)
    return decorator
