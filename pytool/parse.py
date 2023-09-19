import inspect
from typing import Callable, Dict, List

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

def Param(argname: str, type=_void, default=_void, desc:str=_void) -> Callable:
    from functools import wraps
    def decorator(code: Callable):
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
        @wraps(code)
        def wrapper(*args, **kwargs):
            return code(*args, **kwargs)
        return wrapper
    return decorator