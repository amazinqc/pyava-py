from .pyava import Remote, Enum, Class, Module, unwrap, ok


def UserManager() -> Remote:
    return Enum('org.GameServer.logic.player.manager.UserManager')


def GameServerStarter() -> Remote:
    return Class('org.GameServer.GameServerStarter')


def GameManager() -> Remote:
    return Enum('org.GameServer.logic.GameManager')


def saltOut(id: int) -> int:
    return unwrap(Class('org.GameServer.logic.module.User').uidWithoutSalt(id))


def salt(uid: int) -> int:
    return unwrap(Class('org.GameServer.logic.module.User').uidWithSalt(uid))


def getFactionTower(uid: int, faction: str) -> Remote:
    return Module('FactionTower', uid).getUFactionTower(Enum('Faction', faction))


def uids() -> list:
    return [uid for uid in unwrap(UserManager().getUsers().keySet())]


def reloadCfg() -> str:
    unwrap(GameServerStarter().reloadCfg())
    return reloadManagerCfg()


def reloadModule(uid: int, module: str) -> dict:
    return Module(module, uid).load()


def userOnline() -> list:
    return [d['uid'] for d in unwrap(UserManager().getOnlineUsers())]


def reloadManagerCfg(l: str = None) -> str:
    if l is None:
        l = unwrap(Class('org.GameServer.logic.manager.ManagerEnum').values())
        l.pop(0)    # None
    if not l:
        return 'Nothing'
    for m in l:
        ok(Enum('org.GameServer.logic.manager.ManagerEnum', m).manager.onReloadCfg())
    return 'OK'


def user(id: int) -> Remote:
    return User(saltOut(id))


class User(Remote):

    def __init__(self, uid: int) -> Remote:
        original = UserManager().getUser(uid)
        self._data_ = original._data_
        self._method_chain_ = original._method_chain_
        self._args_chain_ = original._args_chain_

    def M(self, module: str) -> Remote:
        return self.getModule(Enum("org.GameServer.logic.module.ModuleType", module))


if __name__ == '__main__':
    u = User(1)
    print(unwrap(u.getName()))
