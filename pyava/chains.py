import json
from typing import Any, Callable, Dict, Generator, List, Self, Tuple, override

from .agent import Agent, AgentError

__all__ = (
    'Entry', 'Accessor', 'Local', 'Class', 'Enum', 'Scope', 'Iter', 'Empty', 'IfElse'
)


def namespace[R: Callable[...]](func: R) -> R:
    from functools import wraps

    @wraps(func)
    def wrapper(*args, proxy=False, **kwargs) -> R | Any:
        if proxy:
            return args[0].__getattr__(func.__name__)(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper


class Jsonable:

    def __json__(self, markers=None) -> Dict[str, Any]:
        '''当前节点转化为JSON可序列化数据'''
        return {}
    
    def expand(self, markers=None, markable: bool = False):
        '''当前节点所代表的完整结构展开为JSON可序列化数据'''
        return {}


class ChainMixin:

    __slots__ = ()

    @override
    def __getattr__(self, name: str):
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

    def __getitem__(self, key: str):
        invoker, field = self.field_search(key)
        return field.get(invoker)

    def __setitem__(self, key: str, value: Any):
        invoker, field = self.field_search(key)
        field.set(invoker, value).unwrap()

    def __call__(self, /, *args: Any, local: str = None) -> Self:
        raise NotImplementedError(f'{self.__class__.__name__}未实现调用逻辑')

    # def __repr__(self) -> str:
    #     return str(self.invoke())

    def _try_freeze(self):
        '''冻结不完整的简化操作节点，一般用于将Node属性简易访问转换为对象的字段访问'''
        pass

    @namespace
    def field_search(self, name: str):
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

    @namespace
    def is_object_class(self) -> bool:
        return Class('java.lang.Object').equals(self).unwrap() is True

    @namespace
    def is_class(self) -> bool:
        return Class('java.lang.Class').isAssignableFrom(self.getClass()).unwrap() is True


class ChainNode(ChainMixin, Jsonable):

    __slots__ = ('_local', '_front')

    def __init__(self) -> None:
        self._local: None | str = None
        self._front: None | ChainNode = None

    @override
    def __json__(self, markers=None) -> Dict:
        return {} if (local := self._local) is None else {'local': local}

    @override
    def expand(self, markers=None, markable: bool = False):
        return transmute(self, markers, markable)


type Chains = ChainNode | List[ChainNode] | Tuple[ChainNode, ...]


class Scannable(Jsonable):

    def scan(self) -> Generator[ChainNode, None, None]:
        '''
        用于扫描特色分支中的Node节点
        '''
        yield None


class Scope(Scannable):

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

    @property
    def result(self) -> ChainNode:
        '''获取作用域的返回节点
        '''
        if self._marked:
            return Class('java.util.Arrays').asList(*self._marked)
        elif self._chains:
            return self._chains[-1]
        else:
            return None

    @property
    def chains(self) -> List[ChainNode]:
        '''获取作用域调用链
        '''
        if not (chains := self._chains):
            raise ValueError('Scope作用域为空')
        if self._marked:
            chains.append(self.result)
        return chains

    def unwrap(self) -> Any:
        '''获取作用域调用链的结果值
        '''
        return Agent.unwrap(Jsonify.dumps(self.chains))

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

    @override
    def scan(self):
        '''扫描作用域的链路节点
        '''
        for node in self.chains:
            yield node

    @override
    def __json__(self, markers=None) -> Dict:
        '''转换作用域的链路节点
        '''
        return transmute(self.chains, markers, markable=False)
    
    @override
    def expand(self, markers=None, markable: bool = False):
        '''展开作用域的链路节点
        '''
        return transmute(self.chains, markers, markable=markable)


class Entry(ChainNode, Scannable):
    '''
    启动入口，如`Class`, `Local`等
    '''

    __slots__ = ('_ref', '_type') + ChainNode.__slots__

    def __init__(self, type: str, ref: str | Scannable, local: str = None, front: ChainNode = None):
        '''初始化入口对象

        参数
        ---
        type: str
            可选项：`local`, `class`, `self`, `iter`
        ref: str | Scannable
            字符串数据，或者对象描述数据，如类名，变量名（待定）
        ---
        '''
        self._ref = ref
        self._type = type
        self._local = local
        self._front = front

    @override
    def __json__(self, markers=None) -> Dict:
        ref = self._ref
        json = {
            'type': self._type,
            'ref': ref.expand(markers) if isinstance(ref, Scannable) else ref,
        }
        if self._local:
            json['local'] = self._local
        return json

    @override
    def scan(self):
        if isinstance(ref := self._ref, Scannable):
            yield from ref.scan()


class Accessor(ChainNode, Scannable):

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
            # args也属于Scannable
            'args': tuple(transmute(o, markers, markable=False) if isinstance(o, ChainNode) else o for o in self._args)
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

    @override
    def scan(self):
        '''遍历当前节点的参数节点'''
        for arg in self._args:
            if isinstance(arg, ChainNode):
                yield arg


class Empty(ChainNode):
    '''空根节点，用于无根链节点
    '''

    @override
    def __getattr__(self, name: str) -> Accessor:
        if name in self.__slots__:
            return super().__getattr__(name)
        return Accessor(None, name=name)


def makefront(root: ChainNode, front: ChainNode):
    while root._front:
        root = root._front
    root._front = front


class Iter(Entry):
    '''
    ```
    for Each in Iter:
        ...
    ```
    '''
    Each = Entry('local', '$_each_in_iter', local='$_each_in_iter')
    ''' Each In Iter '''

    type Range = Tuple[int, int]

    __slots__ = ('_filter',) + Entry.__slots__

    def __init__(self, root: ChainNode | Range, foreach: ChainNode = None):
        '''迭代遍历构造

        参数
        ---
        `root: ChainNode | Range(int, int)
            遍历的对象Iterable/Stream或者数字范围[start,end)

        `foreach: ChainNode`
            遍历的执行操作
        ---
        '''
        if isinstance(root, (tuple, list)):
            root = Iter.range(root)
        scope = Scope()
        if foreach:
            scope(foreach)
        super().__init__(type='iter', ref=scope, front=root)
        self._filter = None

    @staticmethod
    def range(range: Range):
        return Class('java.util.stream.IntStream').range(range[0], range[1]).boxed()
    
    @property
    def _inner_scope(self) -> Scope:
        return self._filter or self._ref

    def foreach(self, foreach: ChainNode):
        '''合并到迭代作用域'''
        self._inner_scope(foreach)
        return self

    def tolist(self):
        '''转化为ArrayList'''
        li = Class('java.util.ArrayList').getDeclaredConstructor().newInstance()
        makefront(self._front, li)   # 创建ArrayList
        self.foreach(li.add(self._inner_scope.result or Iter.Each))
        return li

    def tomap(self, key: ChainNode = None, value: ChainNode = None):
        '''转化为HashMap

        参数
        ---
        `key`  : 键映射，默认`Iter.Each`
        `value`: 值映射，默认`Iter.Each`
        ---
        '''
        mp = Class('java.util.HashMap').getDeclaredConstructor().newInstance()
        makefront(self._front, mp)
        self.foreach(mp.put(key or Iter.Each, value or Iter.Each))
        return mp

    def filter(self, filter: ChainNode):
        self.foreach(IfElse(filter).ifTrue(scope := Scope()))
        self._filter = scope
        return self


class IfElse(Entry):

    class _Branch(Scannable):
        '''if-else分支节点'''
        __slots__ = ('_if', '_true', '_false')

        def __init__(self, condition: ChainNode):
            self._if = condition
            self._true: ChainNode | Scope = None
            self._false: ChainNode | Scope = None

        @override
        def scan(self):
            yield self._if
            for branch in (self._true, self._false):
                if isinstance(branch, ChainNode):
                    yield branch
                elif isinstance(branch, Scope):
                    yield from branch.scan()

        @override
        def expand(self, markers=None, markable: bool = False):
            return {
                'if': self._if and self._if.expand(markers, markable),
                'true': self._true and self._true.expand(markers, markable),
                'false': self._false and self._false.expand(markers, markable),
            }

    def __init__(self, condition: ChainNode):
        '''条件分支表达式'''
        super().__init__(type='if', ref=IfElse._Branch(condition))

    def ifTrue(self, onTrue: Chains):
        self._ref._true = onTrue
        return self

    def ifFalse(self, onFalse: Chains):
        self._ref._false = onFalse
        return self


def Class(clz: str, local: str = None, front: ChainNode = None) -> Entry:
    return Entry('class', clz, local, front=front)


def Enum(clz: str, target: str | int = 0, local: str = None, front: ChainNode = None) -> Accessor:
    if isinstance(target, int):
        return Class('java.lang.reflect.Array', front=front).get(Class(clz).getEnumConstants(), target, local=local)
    if isinstance(target, str):
        return Class(clz, front=front).valueOf(target, local=local)
    raise ValueError('枚举对象必须是`int`或`str`类型')


def Local(ref: str, front: ChainNode = None) -> Entry:
    return Entry('local', ref, front=front)


def flatten(node: ChainNode) -> Generator[ChainNode, Any, None]:
    '''
    展开链路节点

        `flatten_mark` 与 `flatten_scan`通常是一起配合使用的，用于标记重复出现的节点并将后现的节点替换为前者的引用

        `flatten`函数则直接展开，不论是否重复出现
    '''
    if (front := node._front) is not None:
        yield from flatten(front)
    yield node


def flatten_scan(node: ChainNode, markers: Dict[ChainNode, bool | Dict]) -> Generator[ChainNode, Any, None]:
    '''
    扫描并展开链路节点
        一般是非主链路的分支节点，为了在已经统一标记的情况下，仅扫描节点并在合适的位置展开，不再重复标记
    '''
    marker = markers.get(node)
    # 引用标记展开，避免参数节点首次展开被错误截止
    # 只有在当前node节点已经存在引用替换节点时，才中断后续展开，直接返回（已经可替换表示后续都是重复节点，直接引用当前节点即可）
    if marker in (None, False, True):
        # 只要是非引用替换节点状态，都需要继续尝试展开，因为此时还没有引用源节点链路（即引用替换节点的指向）
        if (front := node._front) is not None:
            yield from flatten_scan(front, markers)
    yield node


def flatten_mark(node: ChainNode, markers: Dict[ChainNode, bool]) -> Generator[ChainNode, Any, None]:
    '''展开并标记节点
        展开根链路节点，同时会标记所有扫描到的`ChainNode`节点

    参数
    ---
    `node: ChainNode`
        展开链的根节点（结构上的尾节点，因为链节点是向前引用的）

    `markers: Dict[ChainNode, bool]`
        标记状态统计池
            `False`: 待定标记（首次录入后，待定是否会重复）
            `True` : 确认标记(确认重复标记，在节点解释时可以复用引用)
            `Dict` : 在节点序列化解释的过程中，可能会存在可复用的引用替换节点，属于原节点`True`状态的扩展数据
    ---
    函数返回值
        节点链路展开的生成器
    '''
    marker = markers.get(node)

    if marker is None:      # ①首次录入，展开统计
        # 录入前置节点
        if (front := node._front) is not None:
            yield from flatten_mark(front, markers)
        if isinstance(node, Scannable):
            for scan in node.scan():
                tuple(flatten_mark(scan, markers))
        markers[node] = False
    elif marker is False:   # ②待标记，直接确认标记
        # 修改当前节点为重复标记
        markers[node] = True
    yield node


def chainify(chains: Chains, markers: Dict[ChainNode, bool | Dict] = None, markable: bool = True):
    '''节点链式展开

    参数
    ---
    chain: ChainNode | List[ChainNode]
        展开链节点的根
    markers: Dict[ChainNode, Marker | Accessor]
        标记统计池，可选是否启用标记扫描算法。
    markable: bool
        是否可修改节点标记，避免特殊的分支节点（非链路节点）在延迟展开。

        `flatten_mark`会统一扫描标记所有的节点，而非链路节点只会在`__json__`内，再展开扫描。
        所以展开时不能再二次标记（markable=False），否则导会致错误重复的标记，从而在节点解释时错误地判断引用替换，丢失引用源
    ---
    '''
    single = isinstance(chains, ChainNode)  # 单节点还是多节点(节点作用域)
    if markers is None:  # 仅展开链节点即可
        return flatten(chains) if single else _merge(flatten(chain) for chain in chains)
    elif markable:      # 展开链节点，同时在markers内标记所有扫描的节点（包括非主链路节点）
        return flatten_mark(chains, markers) if single else _merge(flatten_mark(chain, markers) for chain in chains)
    else:               # 扫描并展开链节点到合适位置，不修改标记
        return flatten_scan(chains, markers) if single else _merge(flatten_scan(chain, markers) for chain in chains)


def _merge(nodes):
    '''组合链路节点压缩合并'''
    for chain in nodes:
        yield from chain


def transmute(chains: Chains, markers: Dict[ChainNode, bool | Dict] = None, markable: bool = True):
    '''
    格式化转译`ChainNode`节点链（或作用域），先转为简易的Dict格式，便于使用`Jsonify`生成可解读的json数据
    '''
    cs = tuple(chainify(chains, markers, markable))
    if len(cs) == 1:
        return cs[0]
    return {'chains': cs}


class Jsonify(json.JSONEncoder):

    def __init__(self, *args, markers: Dict[ChainNode, bool | Dict] = None, **kwargs):
        self.markers = markers
        self.refid = 0
        super().__init__(*args, **kwargs)

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Jsonable):
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
        return json.dumps(transmute(chains, markers := {}), cls=cls, separators=(',', ':'), markers=markers)
