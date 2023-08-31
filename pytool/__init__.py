from .pyava import Remote, Class, Enum, ok, unwrap, is_class_object, is_class, Long, Integer
from .agent import JavaAgent
from .tools import *


def variables() -> dict:
    import pytool
    variables = {}
    for key in filter(lambda x: not x.startswith('__'), dir(pytool)):
        variables[key] = type(getattr(pytool, key)).__name__
    variables.pop('variables')
    return variables
