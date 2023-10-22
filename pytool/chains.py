import json
from functools import wraps
from typing import Any, Callable, Dict, Generator, List, Self, Tuple, override

from pytool.agent import Agent, AgentError


def namespace[R](func: Callable[..., R]):
    @wraps(func)
    def wrapper(*args, proxy=False, **kwargs) -> R | Any:
        if proxy:
            return args[0].__getattr__(func.__name__)(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper


class ChainMixin:

    __slots__ = ()

    @override
    def __getattr__(self, name: str) -> 'Accessor':
        if name in self.__slots__:
            return super().__getattr__(name)
        return Accessor(self, name=name)

    @override
    def __setattr__(self, name: str, val: Any):
        if name in self.__slots__:
            return super().__setattr__(name, val)
        if isinstance(val, Scope):  # 域内调用合并
            val(self.getClass().getDeclaredField(name).set(self, val._pop()))
        else:
            self.getClass().getDeclaredField(name).set(self, val).unwrap()

    # def __getitem__(self, key: str) -> Self:
    #     invoker, field = self.field_search(key)
    #     return field.get(invoker)

    # def __setitem__(self, key: str, value: Any) -> None:
    #     invoker, field = self.field_search(key)
    #     self.unwrap(field.set(invoker, value))

    def __call__(self, /, *args: Any, local: str = None) -> Self:
        raise NotImplementedError(f'{self.__class__.__name__}未实现调用逻辑')

    # def __repr__(self) -> str:
    #     return str(self.invoke())

    def _try_freeze(self):
        '''冻结节点，一般用于将Node属性转换为对象的字段访问'''
        pass

    @namespace
    def field_search(self, name: str) -> (Self | None, Self):
        if self.is_class():
            return None, self.getDeclaredField(name)
        clz = self.getClass()
        while True:
            if self.is_object_class():
                raise AttributeError(f'{name}属性不存在')
            field = clz.getDeclaredField(name)
            if field.is_ok():
                return self, field
            clz = clz.getSuperclass()

    @namespace
    def invoke(self) -> Dict[str, Any]:
        self._try_freeze()
        return Agent.invoke(Jsonify.dumps(self))

    @namespace
    def unwrap(self) -> Any:
        self._try_freeze()
        return Agent.unwrap(Jsonify.dumps(self))

    @namespace
    def is_ok(self) -> bool:
        try:
            self.unwrap()
            return True
        except AgentError:
            return False

    @namespace
    def scope(self, scope: 'Scope', mark: bool = False) -> Self:
        '''方便链式调用过程中加入作用域'''
        scope(self, mark=mark)
        return self

    # @namespace
    # def is_object_class(self) -> bool:
    #     return Class('java.lang.Object').equals(self).unwrap() is True

    # @namespace
    # def is_class(self) -> bool:
    #     return Class('java.lang.Class').isAssignableFrom(self.getClass()).unwrap() is True


class ChainNode(ChainMixin):

    __slots__ = ('_local', '_front')

    def __init__(self) -> None:
        self._local: None | str = None
        self._front: None | ChainNode = None

    def __json__(self, markers=None) -> Dict:
        return {} if (local := self._local) is None else {'local': local}


class Entry(ChainNode):
    '''
    启动入口，如`Class`, `Local`等
    '''

    __slots__ = ('_ref', '_type') + ChainNode.__slots__

    def __init__(self, type: str, ref: str, local: str = None, front: ChainNode = None):
        '''初始化入口对象

        参数
        ---
        type: str
            可选项：`local`, `class`, `self`, `iter`
        ref: str | Dict
            字符串数据，或者对象描述数据，如类名，变量名（待定）
        ---
        '''
        self._ref = ref
        self._type = type
        self._local = local
        self._front = front

    @override
    def __json__(self, markers=None) -> Dict:
        json = {'ref': self._ref, 'type': self._type}
        if self._local:
            json['local'] = self._local
        return json


class Accessor(ChainNode):

    __slots__ = ('_name', '_args') + ChainNode.__slots__

    def __init__(self, front: ChainNode, name: str):
        front and front._try_freeze()
        self._name = name
        self._args = None
        self._local = None
        self._front = front

    def __call__(self, /, *args: Any, local=None) -> Self:
        if self._args is not None:
            raise RuntimeError(f'duplicated call with {self._name}')
        for arg in args:
            if isinstance(arg, ChainNode):
                arg._try_freeze()
        self._args = args
        self._local = local
        return self

    @override
    def __json__(self, markers=None) -> Dict:
        json = {
            'method': self._name,
            'args': tuple(jsonify(chainify(o, markers, markable=False)) if isinstance(o, ChainNode) else o for o in self._args)
        }
        if self._local:
            json['local'] = self._local
        return json

    @override
    def _try_freeze(self):
        # 转变为对象字段调用
        if self._args is not None:
            return
        invoker = self._front
        # 补全省略的调用过程
        field = invoker.getClass().getDeclaredField(self._name).get(invoker)
        self._front = field._front
        self._name = field._name
        self._args = field._args
        self._local = None


class Iter(Accessor):

    __slots__ = ('_ref', '_args') + ChainNode.__slots__

    def __init__(self) -> None:
        self._front = None
        self._local = None
        self._ref = []
        self._args = []

    def __getattr__(self, name: str) -> Accessor:
        if name in self.__slots__:
            return super().__getattr__(name)
        return Accessor(None, name=name)

    def filter(self, action: ChainNode):
        self._ref.append('filter')
        self._args.append(action)
        return self

    def map(self, action: ChainNode):
        self._ref.append('map')
        self._args.append(action)
        return self

    def foreach(self, action: ChainNode):
        self._ref.append('foreach')
        self._args.append(action)
        return self

    def collect(self):
        self._ref.append('collect')
        self._args.append(None)

    def __json__(self, markers=None) -> Dict:
        json = {'type': 'iter'}
        json['ref'] = [
            {
                'type': t,
                'chains': chainify(n, markers, False)
            } if n else {
                'type': t
            } for t, n in zip(self._ref, self._args)
        ]
        return json


class Scope:

    def __init__(self) -> None:
        self._chains: List[ChainNode | Any] = []
        self._marked = None

    def mark(self, node: ChainNode = None):
        '''标记当前节点（默认最后一个节点的返回值）需要返回值

        通常在需要返回中间值，或者返回多值时主动标记返回的对象
        '''
        if node is None:
            node = self._chains[-1]
        if not isinstance(node, ChainNode):
            raise TypeError('返回值标记只能是Node类型')
        node._try_freeze()
        if not self._marked:
            self._marked = []
        self._marked.append(node)

    def unwrap(self) -> Any:
        '''获取作用域调用链的结果值
        '''
        if not (chains := self._chains):
            raise ValueError('Scope作用域为空')
        if self._marked:
            chains.append(Class('java.util.Arrays').asList(*self._marked))
        return Agent.unwrap(Jsonify.dumps(chains))

    def __call__(self, node: ChainNode | Any, mark: bool = False) -> Self:
        '''标记作用域
        '''
        if isinstance(node, ChainNode):
            node._try_freeze()
        self._chains.append(node)
        if mark:
            self.mark()
        return self

    def _pop(self):
        '''退回最后包裹的值

        内部使用，在特殊场景下需要合并作用域时，用于包裹目标值并标记作用域节点
        '''
        return self._chains.pop()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs):
        pass


def Class(clz: str, local: str = None) -> Entry:
    return Entry('class', clz, local)


def Enum(clz: str, target: str | int = 0, local: str = None) -> Accessor:
    if isinstance(target, int):
        return Class('java.lang.reflect.Array').get(Class(clz).getEnumConstants(), target, local=local)
    if isinstance(target, str):
        return Class(clz).valueOf(target, local=local)
    raise ValueError('枚举对象必须是`int`或`str`类型')


def Local(ref: str) -> Entry:
    return Entry('local', ref)


def Integer(val: int | str) -> Accessor:
    return Class('java.lang.Integer').valueOf(val)


def Long(val: int | str) -> Accessor:
    return Class('java.lang.Long').valueOf(val)


def flatten(node: ChainNode) -> Generator[ChainNode, None, None]:
    '''展开节点'''
    if (front := node._front) is not None:
        yield from flatten(front)
    yield node


def flatten_scan(node: ChainNode, markers: Dict[ChainNode, bool | Dict]) -> Generator[ChainNode, None, None]:
    '''展开扫描节点'''
    marker = markers.get(node)
    # 引用标记展开，避免参数节点首次展开被错误截止
    if marker in (None, False, True):
        if (front := node._front) is not None:
            yield from flatten_scan(front, markers)
    yield node


def flatten_mark(node: ChainNode, markers: Dict[ChainNode, bool]) -> Generator[ChainNode, None, None]:
    '''展开并标记节点

    参数
    ---
    `node: ChainNode`
        展开链节点

    `markers: Dict[ChainNode, bool]`
        标记状态统计池
            `False`: 待定标记

            `True` : 确认标记

    `remarkable: bool = True`
        引用标记
    ---
    函数返回值
        节点展开的生成器
    '''
    marker = markers.get(node)

    if marker is None:      # ①首次录入，展开统计
        # 录入前置节点
        if (front := node._front) is not None:
            yield from flatten_mark(front, markers)
        # 扫描参数(待定引用标记)
        if isinstance(node, Accessor) and (args := node._args):
            for arg in args:
                if isinstance(arg, ChainNode):
                    tuple(flatten_mark(arg, markers))
        # 录入当前节点
        markers[node] = False
    elif marker is False:   # ②待标记，直接确认标记
        markers[node] = True
    yield node


def chainify(chains: ChainNode | List[ChainNode], markers: Dict[ChainNode, bool | Dict] = None, markable: bool = True) -> Tuple[ChainNode, ...]:
    '''节点链式展开

    参数
    ---
    chain: ChainNode | List[ChainNode]
        展开链节点
    markers: Dict[ChainNode, Marker | Accessor]
        标记统计池，可选是否启用标记扫描算法
    markable: bool
        是否可修改节点标记，避免参数节点的延迟展开（二次标记）导致错误的重复标记
    ---
    '''
    single = isinstance(chains, ChainNode)
    if markers is None:
        return tuple(flatten(chains) if single else _merge(flatten(chain) for chain in chains))
    elif markable:
        return tuple(flatten_mark(chains, markers) if single else _merge(flatten_mark(chain, markers) for chain in chains))
    else:
        return tuple(flatten_scan(chains, markers) if single else _merge(flatten_scan(chain, markers) for chain in chains))


def _merge(nodes):
    for chain in nodes:
        yield from chain


def jsonify(chains: Tuple[ChainNode, ...]):
    if len(chains) == 1:
        return chains[0]
    return {'chains': chains}


class Jsonify(json.JSONEncoder):

    def __init__(self, *args, markers: Dict[ChainNode, bool | Dict] = None, **kwargs):
        self.markers = markers
        self.refid = 0
        super().__init__(*args, **kwargs)

    def default(self, obj: Any) -> Any:
        if isinstance(obj, ChainNode):
            if self.markers is None:
                return obj.__json__()
            marker = self.markers.get(obj)
            if isinstance(marker, dict):
                return marker
            json = obj.__json__(self.markers)
            if marker is True:
                if (local := obj._local) is None:
                    self.refid += 1
                    local = f'${self.refid}'
                json['local'] = local
                # 节点替换
                self.markers[obj] = {'type': 'local', 'ref': local}
            return json
        return super().default(obj)

    @classmethod
    def dumps(cls, chains: ChainNode | List[ChainNode]) -> str:
        return json.dumps(jsonify(chainify(chains, markers := {})), cls=cls, separators=(',', ':'), markers=markers)
