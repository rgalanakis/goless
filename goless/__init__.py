import collections
import stackless
import stacklesslib.util as sutil


class _SyncChannel(object):

    def __init__(self):
        self.c = stackless.channel()

    def send(self, value=None):
        self.c.send(value)

    def recv(self):
        return self.c.receive()

    def recv_ready(self):
        return self.c.balance < 0

    def send_ready(self):
        return self.c.balance > 0


class _BufferedChannel(object):
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

    def __init__(self, size):
        assert isinstance(size, int) and size > 0
        self.maxsize = size
        self.values_deque = collections.deque()
        self.waiting_senders_chan = stackless.channel()
        self.waiting_recvers_chan = stackless.channel()

    def send(self, value=None):
        assert len(self.values_deque) <= self.maxsize
        if self.waiting_recvers_chan.balance < 0:
            assert not self.values_deque
            self.waiting_recvers_chan.send(value)
            return
        if len(self.values_deque) == self.maxsize:
            self.waiting_senders_chan.receive()
        assert len(self.values_deque) < self.maxsize
        self.values_deque.append(value)

    def recv(self):
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


def go(func):
    stackless.tasklet(func)()


class rcase(object):
    def __init__(self, chan, on_selected=None):
        self.chan = chan
        self.on_selected = on_selected

    def fulfilled(self):
        return self.chan.recv_ready()

    def exec_(self):
        val = self.chan.recv()
        if self.on_selected:
            return self.on_selected(val)
        return val


class scase(object):
    def __init__(self, chan, value=None, on_selected=None):
        self.chan = chan
        self.on_selected = on_selected
        self.value = value

    def fulfilled(self):
        return self.chan.send_ready()

    def exec_(self):
        self.chan.send(self.value)
        if self.on_selected:
            self.on_selected()


def select(*cases, **kwargs):
    default = kwargs.pop('default', None)
    while True:
        got = _poll(cases)
        if got is not _NOMATCH:
            return got
        if default is not None:
            return default()

_NOMATCH = object()


def _poll(cases):
    for c in cases:
        if c.fulfilled():
            return c.exec_()
    return _NOMATCH
