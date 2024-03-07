import functools
import inspect
from typing import Callable, Dict, List

from back.json import jsonify

_void = inspect.Signature.empty


def parseargs(code: Callable) -> List[Dict[str, str]]:
    if not callable(code):
        raise TypeError(f'{code!r} is not a callable code')
    signature = inspect.signature(code)
    ps = getattr(code, '__args__', {})
    return [ps.get(name) or _extract(parameter) for name, parameter in signature.parameters.items()]


def _extract(parameter: inspect.Parameter):
    info = {'name': parameter.name}
    if parameter.annotation is not _void:
        info['type'] = _encode(parameter.annotation)
    if parameter.default is not _void:
        info['default'] = _encode(parameter.default)
    return info


def _encode(ins):
    if isinstance(ins, type):
        return ins.__name__
    return str(ins)


def Param(argname: str, type=_void, default=_void, desc: str = _void):
    '''标记参数展示数据'''
    def decorator[C: Callable](code: C) -> C:
        if (ps := getattr(code, '__args__', None)) is None:
            setattr(code, '__args__', ps := {})
        if argname in ps:
            raise ValueError(f'duplicate {argname=}')
        param = inspect.signature(code).parameters.get(argname)
        if param is None:
            raise ValueError(f'unknown {argname=}')
        ps[argname] = (info := _extract(param))
        if type is not _void:
            info['type'] = type
        if default is not _void:
            info['default'] = default
        if desc is not _void:
            info['desc'] = desc
        return code
    return decorator


def TableColumn(name: str, label: str):
    '''标记列表结果的表格列字段信息'''
    def decorator[C: Callable](code: C) -> C:
        is_raw = (cs := getattr(code, '__meta_columns__', None)) is None
        if is_raw:
            @functools.wraps(code)
            def wrapper(*args, **kwargs):
                return {'meta': {'field': 'data', 'columns': cs}, 'data': jsonify(code(*args, **kwargs))}
            setattr(wrapper, '__meta_columns__', cs := [])
        cs.insert(0, {'name': name, 'label': label})
        return wrapper if is_raw else code
    return decorator


def MapColumns(key: str, val: str):
    '''标记字典转列表的表格列字段信息'''
    def decorator[C: Callable](code: C) -> C:
        @functools.wraps(code)
        def wrapper(*args, **kwargs):
            return {'meta': {'field': 'data', 'mapped': True, 'columns': [{'name': 'k', 'label': key}, {'name': 'v', 'label': val}]}, 'data': jsonify(code(*args, **kwargs))}
        return wrapper
    return decorator
