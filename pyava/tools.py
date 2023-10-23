from .chains import Accessor, Class


def Integer(val: int | str) -> Accessor:
    return Class('java.lang.Integer').valueOf(val)


def Long(val: int | str) -> Accessor:
    return Class('java.lang.Long').valueOf(val)


def System() -> Accessor:
    return Class('java.lang.System')


def Objects() -> Accessor:
    return Class('java.util.Objects')
