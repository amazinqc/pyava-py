from typing import Dict
import requests


class AgentThreadLocalAccessor:
    '''
    本地线程共享访问器
    '''

    __slots__ = 'local'

    def __init__(self) -> None:
        import threading
        self.local = threading.local()

    def __set__(self, obj, val) -> None:
        if not isinstance(val, JavaAgent):
            raise TypeError(
                f'agent required type <{type(obj).__name__}>, <{type(val).__name__}> found')
        self.local.agent = val

    def __get__(self, obj, clz) -> 'JavaAgent':
        if hasattr(self.local, 'agent'):
            return self.local.agent
        return None

    def __delete__(self, obj) -> None:
        if hasattr(self.local, 'agent'):
            del self.local.agent


class AgentModuleAccessor:
    '''
    全局模块共享访问器
    '''

    __AGENT_MODULE_NAME__ = 'pyava.agent.debug'
    '''自定义模块依赖名称'''

    def __set__(self, obj, val) -> None:
        if not isinstance(val, JavaAgent):
            raise TypeError(
                f'agent required type <{type(obj).__name__}>, <{type(val).__name__}> found')
        import sys
        module = type(sys)(self.__AGENT_MODULE_NAME__)
        module.agent = self
        sys.modules[self.__AGENT_MODULE_NAME__] = module
        return self

    def __get__(self, obj, clz) -> 'JavaAgent':
        import importlib
        try:
            return importlib.import_module(self.__AGENT_MODULE_NAME__).agent
        except ModuleNotFoundError:
            return None

    def __delete__(self, obj) -> None:
        import sys
        sys.modules.pop(self.__AGENT_MODULE_NAME__, None)


class JavaAgent:
    '''
    执行代理，默认http请求
    '''

    SHARED: 'JavaAgent' = AgentThreadLocalAccessor()
    '''用于从共享环境中访问特定的agent
    '''

    def __init__(self, url, /, *, timeout: int = 60) -> None:
        self.url = url
        self.timeout = timeout

    def debug(self, **kvargs) -> Dict:
        r = requests.get(self.url, kvargs, timeout=self.timeout)
        try:
            return r.json()
        except:
            return {'code': 404, 'message': r.text}

    def __enter__(self) -> 'JavaAgent':
        '''动态自定义模块环境依赖
        '''
        self.SHARED = self
        return self

    def __exit__(self, *args, **kvargs) -> None:
        '''清除模块环境依赖
        '''
        del self.SHARED

    def __str__(self) -> str:
        return f'Agent({self.__dict__})'
