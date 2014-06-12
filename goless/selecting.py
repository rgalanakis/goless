from .backends import current as _be


# noinspection PyPep8Naming,PyShadowingNames
class rcase(object):
    """
    A case that will ``chan.recv()`` when the channel is able to receive.
    """
    def __init__(self, chan):
        self.chan = chan

    def ready(self):
        return self.chan.recv_ready()

    def exec_(self):
        return self.chan.recv()


# noinspection PyPep8Naming,PyShadowingNames
class scase(object):
    """A case that will ``chan.send(value)``
    when the channel is able to send."""
    def __init__(self, chan, value):
        self.chan = chan
        self.value = value

    def ready(self):
        return self.chan.send_ready()

    def exec_(self):
        self.chan.send(self.value)


# noinspection PyPep8Naming
class dcase(object):
    """The default case."""
    def ready(self):
        return False


def select(cases):
    """
    Select the first case that becomes ready.
    If a default case (:class:`goless.dcase`) is present,
    return that if no other cases are ready.
    If there is no default case and no case is ready,
    block until one becomes ready.

    See Go's ``reflect.Select`` method for an analog
    (http://golang.org/pkg/reflect/#Select).

    :param cases: List of case instances, such as
      :class:`goless.rcase`, :class:`goless.scase`, or :class:`goless.dcase`.
    :return: ``(chosen case, received value)``.
      If the chosen case is not an :class:`goless.rcase`, it will be None.
    """
    default = None
    for c in cases:
        if c.ready():
            return c, c.exec_()
        if isinstance(c, dcase):
            assert default is None, 'Only one default case is allowd.'
            default = c
    if default is not None:
        # noinspection PyCallingNonCallable
        return default, None

    while True:
        for c in cases:
            if c.ready():
                return c, c.exec_()
        _be.yield_()
