from .pyava import Remote, Class, Enum, Manager, Module, ok, unwrap, is_object_class
from .agent import JavaAgent
from .tools import *


def variables() -> dict:
    import pytool
    variables = {}
    for key in filter(lambda x: not x.startswith('__'), dir(pytool)):
        variables[key] = type(getattr(pytool, key)).__name__
    variables.pop('variables')
    return variables
