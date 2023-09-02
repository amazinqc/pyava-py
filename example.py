from pytool import *


# import json
# define agent in globals for custom self JavaAgent
# agent = JavaAgent('http://127.0.0.1:1234/LocalPyava')
# if __name__ == '__main__':
#     print(json.dumps(variables(), indent=2))


class DebugInPy(JavaAgent):

    def __init__(self, data, **kv) -> None:
        self.data = data

    def debug(self, **kvargs) -> dict:
        return {'code': 200, 'data': self.data}


if __name__ == '__main__':
    # u = User(1)
    # print(unwrap(u.getName()))
    s = 'from pytool import *;u = User(1);print(unwrap(u.getName()))'

    with DebugInPy('Local Debug Only') as agent:
        print(unwrap(User(1).getName()))
        print(agent.SHARED)
    with DebugInPy('Just `exec` Debug') as agent:
        exec(s, {})
