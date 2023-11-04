from .chains import Accessor, Class


def Integer(val: int | str) -> Accessor:
    return Class('java.lang.Integer').valueOf(val)


def Long(val: int | str) -> Accessor:
    return Class('java.lang.Long').valueOf(val)


System = Class('java.lang.System')


Objects = Class('java.util.Objects')
