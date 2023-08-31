from .pyava import Remote, Enum, Class, unwrap, ok


def UserManager() -> Remote:
    return Enum('org.GameServer.logic.player.manager.UserManager')


def StarterClass() -> Remote:
    return Class('org.GameServer.GameServerStarter')


def GameManager() -> Remote:
    return Enum('org.GameServer.logic.GameManager')


def saltOut(id: int, /) -> int:
    return unwrap(Class('org.GameServer.logic.module.User').uidWithoutSalt(id))


def salt(uid: int, /) -> int:
    return unwrap(Class('org.GameServer.logic.module.User').uidWithSalt(uid))


def uids() -> list:
    return [uid for uid in unwrap(UserManager().getUsers().keySet())]


def userOnline() -> list:
    return [d['uid'] for d in unwrap(UserManager().getOnlineUsers())]


def user(id: int, /) -> Remote:
    return User(saltOut(id))


class User(Remote):

    def __init__(self, uid: int, /) -> Remote:
        original = UserManager().getUser(uid)
        self._data_ = original._data_
        self._method_chain_ = original._method_chain_
        self._args_chain_ = original._args_chain_

    def M(self, module: str, /) -> Remote:
        return self.getModule(Enum("org.GameServer.logic.module.ModuleType", module))


def upper(val: str) -> str:
    return val[:1].upper() + val[1:] if val else val


def Manager(manager: str, /) -> Remote:
    return Enum('org.GameServer.logic.manager.ManagerEnum', upper(manager)).manager


def Module(uid: int, module: str, /) -> Remote:
    return User(uid).M(upper(module))


def reloadCfg() -> str:
    unwrap(StarterClass().reloadCfg())
    return reloadManagerCfg()


def reloadManagerCfg(l: str = None, /) -> str:
    if l is None:
        l = unwrap(Class('org.GameServer.logic.manager.ManagerEnum').values())
        l.pop(0)    # None
    if not l:
        return 'Nothing'
    for m in l:
        ok(Manager(m).onReloadCfg())
    return 'OK'


def Activity(aid: int, /) -> Remote:
    return Manager('Activity').getActivity(aid)
