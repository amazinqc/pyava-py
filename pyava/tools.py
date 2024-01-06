from .chains import Accessor, Class


def Integer(val: int | str, local:str = None) -> Accessor:
    return Class('java.lang.Integer').valueOf(val, local=local)


def Long(val: int | str, local: str = None) -> Accessor:
    return Class('java.lang.Long').valueOf(val, local=local)


System = Class('java.lang.System')


Objects = Class('java.util.Objects')
