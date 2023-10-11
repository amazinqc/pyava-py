from pytool.agent import Agent, HttpAgent

from pytool.chains import *




'''
收集器
[
    {
        data?,
        type?: 'self' | 'local' | 'class' | 'enum' | 'manager' | 'iter',
        method,
        args
    },
    ...
]



链式独立调用
Manager('xx').xxx.xxx.xxx... -> Proxy[Item]
Local('name').xxx.xxx.xxx... -> Proxy[Item]

域式合并调用 Scope[Chains, ...]
with Scope() as scope -> Scope[Val]:
    a = Entry().x.y.z
    # 普通作用域合并
    scope(a.get())
    # 赋值作用域合并
    Enum.xx(a).yy.zz = scope(a, mark=True)
    # 标记值返回
    scope.mark(Class().getX())
    b = Local().getX()
    scope(b)
    ...
scope.unwrap() -> [MarkedValue, ...] | ReturnValue


item = Iter(local | Proxy) -> Proxy[Item]{__call__(self) -> Proxy[List[Item]]}
item.xxx.xxx -> Proxy[Item]


{
    'chains': [
        {
            'ref': 'target.details',
            'type': 'local or class',
            'local'?: 'var1'
        },
        {
            'method': 'method name',
            'args': [1, 2, 3],
            'local'?: 'var2'
        },
        {
            'ref': 'target.details',
            'type': 'iter',
            'method': 'iter method',
            'args': [1, 2, 3],
            'local'?: 'var3', 
        }
    ]
}

'''


class DebugInPy(Agent):

    def __init__(self, *args, **kvargs) -> None:
        pass

    def debug(self, data) -> dict:
        return {'code': 200, 'data': data}


if __name__ == '__main__':

    with DebugInPy('Local Debug Only') as agent:
        ...

    # with HttpAgent('http://127.0.0.1/LocalDebugTest'):
        with Scope() as scope:
            zero = Integer(0)
            csys = Class('java.lang.System')
            a = csys.getProperty('a', 'default a')
            cstr = Class('java.lang.String')
            scope(csys.setProperty('b', cstr.valueOf(zero)))
            scope(a, mark=True)
            # Long(2 ** 10).value = 2 ** 10
            Long(2 ** 10).value = scope(Long(2 ** 10))
        r = scope.unwrap()
    print(json.dumps(json.loads(r), indent=2))
    '''
```json
{
  "chains": [
    {
      "ref": "java.lang.System",
      "type": "class",
      "local": "$1"
    },
    {
      "method": "setProperty",
      "args": [
        "b",
        {
          "chains": [
            {
              "ref": "java.lang.String",
              "type": "class"
            },
            {
              "method": "valueOf",
              "args": [
                {
                  "chains": [
                    {
                      "ref": "java.lang.Integer",
                      "type": "class"
                    },
                    {
                      "method": "valueOf",
                      "args": [
                        0
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "local",
      "ref": "$1"
    },
    {
      "method": "getProperty",
      "args": [
        "a",
        "default a"
      ],
      "local": "$2"
    },
    {
      "ref": "java.lang.Long",
      "type": "class"
    },
    {
      "method": "valueOf",
      "args": [
        1024
      ],
      "local": "$3"
    },
    {
      "method": "getClass",
      "args": []
    },
    {
      "method": "getDeclaredField",
      "args": [
        "value"
      ]
    },
    {
      "method": "set",
      "args": [
        {
          "type": "local",
          "ref": "$3"
        },
        {
          "chains": [
            {
              "ref": "java.lang.Long",
              "type": "class"
            },
            {
              "method": "valueOf",
              "args": [
                1024
              ]
            }
          ]
        }
      ]
    },
    {
      "ref": "java.util.Arrays",
      "type": "class"
    },
    {
      "method": "asList",
      "args": [
        {
          "type": "local",
          "ref": "$2"
        }
      ]
    }
  ]
}
```
    '''

