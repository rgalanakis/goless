import collections as _collections
import sys

from .backends import current as _be


class ChannelClosed(Exception):
    """Exception raised when send is called on a closed channel,
    or recv is called on a closed channel with an empty buffer."""


class BaseChannel(object):
    _nickname = None

    def __init__(self):
        self._closed = False

    def send(self, value=None):
        if self._closed:
            raise ChannelClosed()
        self._send(value)

    def _send(self, value):
        raise NotImplementedError()

    def recv(self):
        if self._closed and not self.recv_ready():
            raise ChannelClosed()
        got = self._recv()
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


class BufferedChannel(BaseChannel):
    """
    BufferedChannel has several situations it must handle.

    When sending:

    1. If there is a receiver waiting send the value through the channel.
       A waiting receiver indicates the buffer was empty.
       It's uncertain in this case if there will be a context switch 
       (blocking the current task) or not.
    2. Else if there is no more room in the buffer,
       also send the value through the channel,
       blocking until a receiver for the value is available.
    3. Otherwise just append the value to the deque returning immediately.

    When receiving:

    1. If the buffer has items, pop and return the first value.
       Before returning, if there is a sender waiting,
       receive its value and append it to the buffer.
    2. Else just receive on the channel,
       blocking until a sender is available.
       Return the value from the sender.
    """
    _nickname = 'gobufchan'

    def __init__(self, size):
        assert isinstance(size, int)
        BaseChannel.__init__(self)
        self.maxsize = size
        self.values_deque = _collections.deque()
        self.waiting_chan = _be.channel()

    def _send(self, value):
        buffer_size = len(self.values_deque)
        assert buffer_size <= self.maxsize
        assert ((self.waiting_chan.balance < 0 and buffer_size == 0)
                or (self.waiting_chan.balance > 0 and buffer_size == self.maxsize)
                or self.waiting_chan.balance == 0)
        if self.waiting_chan.balance < 0 or buffer_size == self.maxsize:
            self.waiting_chan.send(value)
        else:
            assert buffer_size < self.maxsize
            self.values_deque.append(value)

    def _recv(self):
        if self.values_deque:
            value = self.values_deque.popleft()
            if self.waiting_chan.balance > 0:
                self.values_deque.append(self.waiting_chan.receive())
        else:
            value = self.waiting_chan.receive()
        return value

    def recv_ready(self):
        return self.values_deque or self.waiting_chan.balance > 0

    def send_ready(self):
        return len(self.values_deque) < self.maxsize or self.waiting_chan.balance < 0


class SyncChannel(BufferedChannel):
    """
    Channel that behaves synchronously.
    A recv blocks until a sender is available,
    and a sender blocks until a receiver is available.
    Implemented as a special case of BufferedChannel
    where the buffer size is 0.
    """
    _nickname = 'gosyncchan'

    def __init__(self):
        BufferedChannel.__init__(self, 0)


class AsyncChannel(BufferedChannel):
    """
    A channel where send never blocks,
    and recv blocks if there are no items in the buffer.
    Implemented as a special case of BufferedChannel
    where the buffer size is sys.maxint.
    """
    _nickname = 'goasyncchan'

    def __init__(self):
        BufferedChannel.__init__(self, sys.maxint)


def bchan(size=0):
    """
    Returns a bidirectional channel.
    A 0 or None size indicates a blocking channel
    (``send`` will block until a receiver is available,
    ``recv`` will block until a sender is available).
    A positive integer value will return a channel with a buffer.
    Once the buffer is filled, ``send`` will block.
    When the buffer is empty, ``recv`` will block.

    :rtype: BaseChannel
    """
    if not size:
        return SyncChannel()
    if size < 0:
        return AsyncChannel()
    return BufferedChannel(size)

chan = bchan
