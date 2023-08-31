from typing import Dict
import requests

AGENT_MODULE_NAME = 'pyava.agent.debug'
'''自定义模块依赖名称'''


class JavaAgent:
    '''
    执行代理，默认http请求
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

    def __enter__(self) -> None:
        '''动态自定义模块环境依赖
        '''
        import sys
        module = type(sys)(AGENT_MODULE_NAME)
        module.agent = self
        sys.modules[AGENT_MODULE_NAME] = module

    def __exit__(self, *args, **kvargs) -> None:
        '''清除模块环境依赖
        '''
        import sys
        sys.modules.pop(AGENT_MODULE_NAME, None)
