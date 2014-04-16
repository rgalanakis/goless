import collections as _collections
import stackless as _stackless

from .debug import DEBUG, debug

schannel = _stackless.channel
if DEBUG:
    # noinspection PyPep8Naming
    class schannel(_stackless.channel):
        def send(self, value):
            debug('schan sending')
            _stackless.channel.send(self, value)
            debug('schan sent')

        def receive(self):
            debug('schan recving')
            got = _stackless.channel.receive(self)
            debug('schan recved')
            return got


class ChannelClosed(Exception):
    """Exception raised when send is called on a closed channel,
    or recv is called on a closed channel with an empty buffer."""


class _BaseChannel(object):
    _nickname = None

    def __init__(self):
        self._closed = False

    def send(self, value=None):
        debug('%s sending %s', self._nickname, value)
        if self._closed:
            debug('send failed, %s is closed!', self._nickname)
            raise ChannelClosed()
        self._send(value)
        debug('%s sent', self._nickname)

    def _send(self, value):
        raise NotImplementedError()

    def recv(self):
        debug('%s recving', self._nickname)
        if self._closed and not self.recv_ready():
            debug('recv failed, %s is closed and empty.', self._nickname)
            raise ChannelClosed()
        got = self._recv()
        debug('%s recved %s', self._nickname, got)
        return got

    def _recv(self):
        raise NotImplementedError()

    def recv_ready(self):
        """Return True if there is a sender waiting,
        or there are items in the buffer."""
        raise NotImplementedError()

    def send_ready(self):
        """Return True if a receiver is waiting,
        or the buffer has room."""

    def close(self):
        """Closes the channel, not allowing further communication.
        See documentation for details about closed channel behavior."""
        self._closed = True

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.recv()
        except ChannelClosed:
            raise StopIteration


class _SyncChannel(_BaseChannel):
    """Channel that behaves synchronously.
    A recv blocks until a sender is available,
    and a sender blocks until a recver is available.
    """
    _nickname = 'gosyncchan'

    def __init__(self):
        _BaseChannel.__init__(self)
        self.c = schannel()

    def _send(self, value):
        self.c.send(value)

    def _recv(self):
        return self.c.receive()

    def recv_ready(self):
        return self.c.balance > 0

    def send_ready(self):
        return self.c.balance < 0


class _AsyncChannel(_BaseChannel):
    """
    A channel where send never blocks,
    and recv blocks if there are no items in the buffer.
    """
    _nickname = 'goasyncchan'

    def __init__(self):
        _BaseChannel.__init__(self)
        self.c = schannel()
        self.q = _collections.deque()

    def _send(self, value):
        self.q.append(value)

    def _recv(self):
        if not self.q:
            return self.c.receive()
        return self.q.popleft()

    def send_ready(self):
        return True

    def recv_ready(self):
        return bool(self.q)


class _BufferedChannel(_BaseChannel):
    """
    BufferedChannel has several situations it must handle:

    1. When sending, if there is room in the buffer, just append the value and return.
    2. When sending, if the buffer is full, block until told there is room in the buffer
       and then append the value.
       The recv method will signal the sender when there is room (see #4).
    3. When sending, if there are recvers waiting (see #6),
       send the value directly to the first waiting recver.
       Bypass the bugger entirely. The buffer should always be empty in this case.
    4. Whenever recving, if there are senders waiting for room in the buffer (see #2),
       signal the first one after popping a value.
    5. When recving, if there is an item in the buffer, pop it off,
       execute step #4, and return the popped value.
    6. When recving, if there is no item in the buffer,
       block until an item is recved (see #3).
       This bypasses the buffer entirely because we send the value through the channel.
    """
    _nickname = 'gobufchan'

    def __init__(self, size):
        assert isinstance(size, int) and size > 0
        _BaseChannel.__init__(self)
        self.maxsize = size
        self.values_deque = _collections.deque()
        self.waiting_senders_chan = schannel()
        self.waiting_recvers_chan = schannel()

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
    A 0 or None size indicates a blocking channel
    (``send`` will block until a receiver is available,
    ``recv`` will block until a sender is available).
    A positive integer value will return a channel with a buffer.
    Once the buffer is filled, ``send`` will block.
    When the buffer is empty, ``recv`` will block.

    :rtype: _BaseChannel
    """
    if size in (None, 0):
        return _SyncChannel()
    if size < 0:
        return _AsyncChannel()
    return _BufferedChannel(size)

chan = bchan
