import collections as _collections
import stackless as _stackless


DEBUG = True


def debug(s, *args):
    print s % args


_channel = _stackless.channel
if DEBUG:
    class _Channel(_stackless.channel):
        def send(self, value):
            debug('schan sending')
            _stackless.channel.send(self, value)
            debug('schan sent')

        def receive(self):
            debug('schan recving')
            got = _stackless.channel.receive(self)
            debug('schan recved')
            return got


def go(func):
    """Run a function in a new tasklet, like a goroutine."""
    _stackless.tasklet(func)()


class _BaseChannel(object):
    _nickname = None

    def send(self, value=None):
        debug('%s sending %s', self._nickname, value)
        self._send(value)
        debug('%s sent', self._nickname)

    def _send(self, value):
        raise NotImplementedError()

    def recv(self):
        debug('%s recving', self._nickname)
        got = self._recv()
        debug('%s recved %s', self._nickname, got)
        return got

    def _recv(self):
        raise NotImplementedError()


class _SyncChannel(_BaseChannel):
    _nickname = 'gosyncchan'

    def __init__(self):
        _BaseChannel.__init__(self)
        self.c = _stackless.channel()

    def _send(self, value):
        self.c.send(value)

    def _recv(self):
        return self.c.receive()

    def recv_ready(self):
        return self.c.balance > 0

    def send_ready(self):
        return self.c.balance < 0


class _BufferedChannel(_BaseChannel):
    """
    BufferedChannel has several situations it must handle:

    1. When sending, if there is room in the deque, just append the value and return.
    2. When sending, if the deque is full, block until told there is room in the queue
       and then append the value.
       The recv method will signal the sender when there is room (see #4).
    3. When sending, if there are recvers waiting (see #6),
       send the value directly to the first waiting recver.
       Bypass the deque entirely. The deque should always be empty in this case.
    4. Whenever recving, if there are senders waiting for room in the queue (see #2),
       signal the first one after popping a value.
    5. When recving, if there is an item in the deque, pop it off,
       execute step #4, and return the popped value.
    6. When recving, if there is no item in the queue,
       block until an item is recved (see #3).
       This bypasses the deque entirely because we send the value through the channel.
    """
    _nickname = 'gobufchan'

    def __init__(self, size):
        assert isinstance(size, int) and size > 0
        _BaseChannel.__init__(self)
        self.maxsize = size
        self.values_deque = _collections.deque()
        self.waiting_senders_chan = _stackless.channel()
        self.waiting_recvers_chan = _stackless.channel()

    def _send(self, value):
        assert len(self.values_deque) <= self.maxsize
        if self.waiting_recvers_chan.balance < 0:
            assert not self.values_deque
            self.waiting_recvers_chan.send(value)
            return
        if len(self.values_deque) == self.maxsize:
            self.waiting_senders_chan.receive()
        assert len(self.values_deque) < self.maxsize
        self.values_deque.append(value)

    def _recv(self):
        if self.values_deque:
            value = self.values_deque.popleft()
        else:
            value = self.waiting_recvers_chan.receive()
        if self.waiting_senders_chan.balance < 0:
            self.waiting_senders_chan.send(None)
        return value

    def recv_ready(self):
        return self.values_deque or self.waiting_senders_chan.balance < 0

    def send_ready(self):
        return len(self.values_deque) < self.maxsize or self.waiting_recvers_chan.balance < 0


def bchan(size=None):
    """
    Returns a bidirectional channel.
    A 0 or None size indicates a blocking channel (send will block until a recveiver is available).
    A positive integer value will give a channel with a queue until it begins to block.
    """
    if not size:
        return _SyncChannel()
    return _BufferedChannel(size)

chan = bchan


# noinspection PyPep8Naming,PyShadowingNames
class rcase(object):
    def __init__(self, chan, on_selected=None):
        self.chan = chan
        self.on_selected = on_selected

    def ready(self):
        return self.chan.recv_ready()

    def exec_(self):
        val = self.chan.recv()
        if self.on_selected:
            return self.on_selected(val)
        return val


# noinspection PyPep8Naming,PyShadowingNames
class scase(object):
    def __init__(self, chan, value=None, on_selected=None):
        self.chan = chan
        self.on_selected = on_selected
        self.value = value

    def ready(self):
        return self.chan.send_ready()

    def exec_(self):
        self.chan.send(self.value)
        if self.on_selected:
            self.on_selected()


def select(*cases, **kwargs):
    for c in cases:
        if c.ready():
            return c.exec_()
    default = kwargs.pop('default', None)
    if default is not None:
        # noinspection PyCallingNonCallable
        return default()

    # while True:
    #     for c in cases:
    #         if c.ready():
    #             return c.exec_()
    #     _stackless.run(0)

    # def handle_case(case):
    #     pass#case.ready_signal.connect(lambda: syncchannel.send(case))
    #
    # for c in cases:
    #     handle_case(c)
    #
    # debug('select receiving')
    # case_to_exec = syncchannel.receive()
    # # try:
    # #     case_to_exec = syncchannel.receive()
    # # except RuntimeError:
    # #     assert _stackless.getcurrent() is _stackless.main
    # #     result = []
    # #     bgtasklet = _stackless.tasklet(lambda: result.append(syncchannel.receive()))()
    # #     while bgtasklet.alive:
    # #         _stackless.run(0)
    # #     case_to_exec = result[0]
    # return case_to_exec.exec_()
