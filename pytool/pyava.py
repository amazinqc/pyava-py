from typing import Any, Dict
import json
import copy

from .agent import JavaAgent


class Remote():

    __slots__ = '_data_', '_method_chain_', '_args_chain_'

    def __init__(self):
        self._data_ = {}
        self._method_chain_ = []
        self._args_chain_ = []

    def __getattr__(self, _name: str) -> 'Remote':
        other = self._autofield_and_copy_()
        other._method_chain_.append(_name)
        return other

    def __setattr__(self, _name: str, val: Any):
        if _name in Remote.__slots__:
            return super().__setattr__(_name, val)
        unwrap(self.getClass().getDeclaredField(_name).set(self, val))

    def __getitem__(self, key: str) -> 'Remote':
        invoker, field = self._field_(key)
        return field.get(invoker)

    def __setitem__(self, key: str, value: Any):
        invoker, field = self._field_(key)
        unwrap(field.set(invoker, value))

    def __call__(self, /, *args: Any) -> 'Remote':
        self._args_chain_.append(tuple(args))
        return self

    def __repr__(self) -> str:
        return str(self._invoke_())

    def __deepcopy__(self, memo: Dict) -> 'Remote':
        copied = Remote()
        copied._data_.update(self._data_)
        copied._method_chain_.extend(self._method_chain_)
        copied._args_chain_.extend(self._args_chain_)
        return copied

    def _autofield_and_copy_(self) -> 'Remote':
        other = copy.deepcopy(self)
        if len(other._method_chain_) > len(other._args_chain_):
            last_field = other._method_chain_.pop()
            other = other.getClass().getDeclaredField(last_field).get(other)
        return other

    def _collect_(self) -> Dict:
        other = self._autofield_and_copy_()
        data = other._data_
        data['method_chain'] = json.dumps(other._method_chain_)
        data['args_chain'] = json.dumps(
            other._args_chain_, default=lambda x: x._collect_() if isinstance(x, Remote) else x)
        return data

    def _invoke_(self) -> str or Dict:
        agent: JavaAgent = globals().get('agent', JavaAgent())
        return agent.debug(**self._collect_())

    def _field_(self, field: str) -> ('Remote', 'Remote'):
        clz = self.getClass()
        selfIsClass = unwrap(
            Class('java.lang.Class').isAssignableFrom(clz)) is True
        if selfIsClass:
            return None, self.getDeclaredField(field)

        while True:
            if is_object_class(clz):
                raise AttributeError(f'{field}属性不存在')
            field = clz.getDeclaredField(field)
            if ok(field):
                return self, field
            clz = clz.getSuperclass()

    def _module_(self, module: str, uid: int) -> 'Remote':
        if self._data_:
            raise ValueError("已实例的对象不可以重复使用")
        self._data_['module'] = module
        self._data_['uid'] = uid
        return self

    def _manager_(self, manager: str) -> 'Remote':
        if self._data_:
            raise ValueError("已实例的对象不可以重复使用")
        self._data_['manager'] = manager
        return self

    def _clazz_(self, clazz: str) -> 'Remote':
        if self._data_:
            raise ValueError("已实例的对象不可以重复使用")
        self._data_['class'] = clazz
        return self

    def _enum_(self, enum, target: str or int = 0) -> 'Remote':
        if self._data_:
            raise ValueError("已实例的对象不可以重复使用")
        if target is None:
            target = 0
        if isinstance(target, int):
            self._data_['ordinal'] = target
        elif isinstance(target, str):
            self._data_['name'] = target
        else:
            raise TypeError("枚举只能指定实例名或实例序号")
        self._data_['enum'] = enum
        return self


def Module(module: str, uid: int) -> Remote:
    return Remote()._module_(upper(module), uid)


def Manager(manager: str) -> Remote:
    return Remote()._manager_(upper(manager))


def Class(clazz: str) -> Remote:
    return Remote()._clazz_(clazz)


def Enum(enum, target: str or int = 0) -> Remote:
    return Remote()._enum_(enum, target)


def unwrap(target: Remote) -> Any:
    ret = target._invoke_()
    if ret.get('code') == 200:
        return ret.get('data')
    raise SystemError(ret)


def ok(target: Remote) -> Any:
    ret = target._invoke_()
    return ret.get('code') == 200


def is_object_class(clz: 'Remote') -> bool:
    return unwrap(Class('java.lang.Object').equals(clz)) is True


def upper(val: str) -> str:
    return val[:1].upper() + val[1:] if val else val
