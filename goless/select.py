from .backends import current as _be


# noinspection PyPep8Naming,PyShadowingNames
class rcase(object):
    def __init__(self, chan):
        self.chan = chan

    def ready(self):
        return self.chan.recv_ready()

    def exec_(self):
        return self.chan.recv()


# noinspection PyPep8Naming,PyShadowingNames
class scase(object):
    def __init__(self, chan, value):
        self.chan = chan
        self.value = value

    def ready(self):
        return self.chan.send_ready()

    def exec_(self):
        self.chan.send(self.value)


# noinspection PyPep8Naming
class dcase(object):
    def ready(self):
        return False


def select(cases):
    default = None
    for c in cases:
        if c.ready():
            return c, c.exec_()
        if isinstance(c, dcase):
            default = c
    if default is not None:
        # noinspection PyCallingNonCallable
        return default, None

    while True:
        for c in cases:
            if c.ready():
                return c, c.exec_()
        _be.yield_()
