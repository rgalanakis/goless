from .backends import current as _be, Deadlock as _Deadlock
from .channels import ChannelClosed


# noinspection PyPep8Naming,PyShadowingNames
class rcase(object):
    """
    A case that will ``chan.recv()`` when the channel is able to receive.
    """
    def __init__(self, chan):
        self.chan = chan

    def ready(self):
        return self.chan is not None and (self.chan._closed or self.chan.recv_ready())

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
        return self.chan is not None and (self.chan._closed or self.chan.send_ready())

    def exec_(self):
        self.chan.send(self.value)


# noinspection PyPep8Naming
class dcase(object):
    """The default case."""
    def ready(self):
        return False


def select_ok(*cases):
    """
    Select the first case that becomes ready, including an ``ok`` indication.
    This is the same as the ``select`` method except than an ``ok`` indication
    is included, allowing checks for closed channels.

    :param cases: List of case instances, such as
      :class:`goless.rcase`, :class:`goless.scase`, or :class:`goless.dcase`.
    :return: ``(chosen case, received value, ok indication)``.
      If the chosen case is not an :class:`goless.rcase`, it will be None.
    """
    if len(cases) == 0:
        return
    # If the first argument is a list, it should be the only argument
    if isinstance(cases[0], list):
        if len(cases) != 1:
            raise TypeError('Select can be called either with a list of cases '
                            'or multiple case arguments, but not both.')
        cases = cases[0]
        if not cases:
            # Handle the case of an empty list as an argument,
            # and prevent the raising of a SystemError by libev.
            return

    default = None
    for c in cases:
        if c.ready():
            try:
                return c, c.exec_(), True
            except ChannelClosed:
                return c, None, False
        if isinstance(c, dcase):
            assert default is None, 'Only one default case is allowd.'
            default = c
    if default is not None:
        # noinspection PyCallingNonCallable
        return default, None, True

    # We need to check for deadlocks before selecting.
    # We can't rely on the underlying backend to do it,
    # as we do for channels, since we don't do an actual send or recv here.
    # It's possible to still have a deadlock unless we move the check into
    # the loop, but since the check is slow
    # (gevent doesn't provide a fast way), let's leave it out here.
    if _be.would_deadlock():
        raise _Deadlock('No other tasklets running, cannot select.')
    while True:
        for c in cases:
            if c.ready():
                try:
                    return c, c.exec_(), True
                except ChannelClosed:
                    return c, None, False
        _be.yield_()


def select(*cases):
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
    result = select_ok(*cases)
    if result is not None:
        chosen, value, ok = result
        if not ok:
            raise ChannelClosed()
        result = chosen, value
    return result
