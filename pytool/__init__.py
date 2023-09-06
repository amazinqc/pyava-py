from .pyava import Remote, Class, Enum, ok, unwrap, is_class_object, is_class, Long, Integer
from .agent import JavaAgent
from .tools import *

__all__ = [
    'Long', 'Integer',
    'Class', 'Enum', 'Manager', 'Module',
    'ok', 'unwrap', 'is_class_object', 'is_class', 'upper',
    'salt', 'saltOut',
    'UserManager', 'StarterClass', 'GameManager', 'Activity', 'User', 'user',
    'userOnline', 'uids', 'reloadCfg', 'reloadManagerCfg'
]


def variables() -> dict:
    import pytool
    variables = {}
    for key in __all__:
        variables[key] = type(getattr(pytool, key)).__name__
    return variables
