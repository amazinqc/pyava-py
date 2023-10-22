from typing import Any, Dict, Self

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
        if not isinstance(val, Agent):
            raise TypeError(
                f'agent required type <{type(obj).__name__}>, <{type(val).__name__}> found')
        self.local.agent = val

    def __get__(self, obj, clz) -> 'Agent':
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
        if not isinstance(val, Agent):
            raise TypeError(
                f'agent required type <{type(obj).__name__}>, <{type(val).__name__}> found')
        import sys
        module = type(sys)(self.__AGENT_MODULE_NAME__)
        module.agent = self
        sys.modules[self.__AGENT_MODULE_NAME__] = module
        return self

    def __get__(self, obj, clz) -> 'Agent':
        import importlib
        try:
            return importlib.import_module(self.__AGENT_MODULE_NAME__).agent
        except ModuleNotFoundError:
            return None

    def __delete__(self, obj) -> None:
        import sys
        sys.modules.pop(self.__AGENT_MODULE_NAME__, None)


class AgentError(BaseException):
    pass


class Agent:

    _SHARED: Self = AgentThreadLocalAccessor()
    '''用于从共享环境中访问特定的agent
    '''

    @staticmethod
    def unwrap(data) -> Any:
        '''执行目标方法，并解包返回数据'''
        ret = Agent.invoke(data)
        if ret.get('code') == 200:
            return ret.get('data')
        raise AgentError(ret)

    @classmethod
    def invoke(cls, data):
        '''执行目标方法，返回可能附带额外信息的结果'''
        agent = cls._SHARED
        if agent is not None:
            return agent.debug(data)
        else:
            return {'No Agent': data}

    def debug(self, data) -> dict[str, Any]:
        pass

    def __enter__(self) -> Self:
        '''动态自定义模块环境依赖
        '''
        self._SHARED = self
        return self

    def __exit__(self, *args, **kvargs) -> None:
        '''清除模块环境依赖
        '''
        del self._SHARED

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.__dict__})'


class HttpAgent(Agent):
    '''HTTP请求执行代理

    默认post请求
    '''

    def __init__(self, url, /, *, timeout: int = 60) -> None:
        self.url = url
        self.timeout = timeout

    def debug(self, data) -> Dict[str, Any]:
        r = requests.post(self.url, json={'json': data}, timeout=self.timeout)
        try:
            return r.json()
        except:
            return {'code': 404, 'message': r.text}
