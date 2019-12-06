from .backends import GolessException
from .channels import BufferedChannel
from .selecting import rcase


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
        if self._counter == 0 and self._chan is not None:
            self._chan.send()

    def wait(self):
        """
        Blocks until the WaitGroup counter is 0.
        """
        self._check_finalized()
        if self._counter == 0:
            return
        self._chan = BufferedChannel(1)
        self._chan.recv()

    def wait_case(self):
        """
        Returns a case object that can be used in goless.select.
        The case executes when the wait group is done.
        """
        self._check_finalized()
        if self._counter == 0:
            # Make an immediately ready channel.
            # We would like to use dcase but there can be only one in a select so it'd be naughty.
            chan = BufferedChannel(1)
            chan.send()
            return rcase(chan)

        self._chan = BufferedChannel(1)
        return rcase(self._chan)

    def _check_finalized(self):
        if self._finalized:
            raise InvalidWaitGroup('wait can only be called once')
        self._finalized = True


class InvalidWaitGroup(GolessException):
    pass
