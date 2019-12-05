from .backends import GolessException
from .channels import SyncChannel


class WaitGroup(object):
    """
    WaitGroup implementation for goless.
    See https://golang.org/pkg/sync/#WaitGroup

    This supports the most common WaitGroup use case,
    where it is used for fanning out goroutines for an operation.
    It does not support some more exotic use cases like negative `Add` values
    and triggering `wait` multiple times.

    Its known limitiations/differences from Go's WaitGroup are:
    - `add` value must be positive.
    - `wait` can only be called once (multiple goroutines cannot wait for
      the same wait group).
    - `add` cannot be called after `wait` (this can lead to bugs- add everything up front).
    These can be fixed in the future if needed,
    but in years of Go programming I've only needed this pattern.
    """

    def __init__(self, delta=None):
        self._is_done = False
        self._counter = 0
        self._chan = None
        self._finalized = False
        if delta is not None:
            self.add(delta)

    def add(self, delta):
        """
        Adds delta, which may be negative, to the WaitGroup counter.
        If the counter becomes zero, all goroutines blocked on Wait
        are released. If the counter goes negative, add panics.
        """
        if delta <= 0:
            raise InvalidWaitGroup('add delta must be positive')
        if self._finalized:
            raise InvalidWaitGroup('add cannot be called after wait')
        self._counter += delta

    def done(self):
        """
        Decrements the WaitGroup counter by one.
        """
        self._counter -= 1
        if self._counter < 0:
            raise InvalidWaitGroup('done called for a task that was never added')
        if self._counter == 0:
            self._is_done = True
            if self._chan is not None:
                self._chan.send()

    def wait(self):
        """
        Blocks until the WaitGroup counter is 0.
        """
        if self._finalized:
            raise InvalidWaitGroup('wait can only be called once')

        self._finalized = True
        if self._counter == 0:
            self._is_done = True
            return
        self._chan = SyncChannel()
        self._chan.recv()


class InvalidWaitGroup(GolessException):
    pass
