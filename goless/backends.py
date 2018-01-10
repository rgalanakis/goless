import contextlib as _contextlib
import gc as _gc
import os as _os
import platform as _platform
import sys as _sys
import time as _time

from . import compat


class GolessException(Exception):
    pass


class Deadlock(GolessException):
    def __init__(self, msg):
        Exception.__init__(self, msg)


@_contextlib.contextmanager
def as_deadlock(errtypes):
    try:
        yield
    except errtypes as e:
        ex = Deadlock('Error raised by backend due to detected deadlock. '
                      'Original error: %r' % e)
        compat.reraise(Deadlock, ex, e)


class Backend(object):

    def shortname(self):
        return type(self).__name__

    def start(self, func, *args, **kwargs):
        """Starts a tasklet/greenlet."""
        raise NotImplementedError()

    def run(self, func, *args, **kwargs):
        """Runs a tasklet up until it blocks or finishes."""
        raise NotImplementedError()

    def channel(self):
        """Returns a new channel."""
        raise NotImplementedError()

    def yield_(self):
        """Yields control for other tasklets/greenlets to run.
        If none are available, do nothing.
        """
        raise NotImplementedError()

    def sleep(self, secs):
        """Sleep the current goroutine."""
        raise NotImplementedError()

    def resume(self, tasklet):
        """Runs the given tasklet/greenlet immediately."""
        raise NotImplementedError()

    def propagate_exc(self, errtype, *args):
        """Propagates an exception (created via ``errtype(*args)``)
        so the program hears it and it doesn't die lonely in a tasklet."""
        raise NotImplementedError()

    def would_deadlock(self):
        """Return True if a send or receive would deadlock
        (current tasklet/greenlet is the last one running)."""
        raise NotImplementedError()


# We can't easily use stackless on our CI,
# so don't worry about covering it.
# For sleep implementation, credit to
# http://www.grant-olson.net/files/why_stackless.html#the-stackless-version-of-the-code
def _make_stackless():  # pragma: no cover
    import stackless

    class SleepingTaskletManager(object):
        def __init__(self):
            self.next_sleep_id = 0
            self.sleeping_tasklets = []
            self.sleeping_ticks = 0
            self._run_tasklet = None
            self.running = False

        def _run(self):
            while self.has_sleeping_tasklets():
                print('checking for waking')
                end_time = self.sleeping_tasklets[0][0]
                while end_time <= self.sleeping_ticks and self.has_sleeping_tasklets():
                    print('et', end_time, 'ticks', self.sleeping_ticks, 'sleeping', self.sleeping_tasklets)
                    channel = self.sleeping_tasklets[0][2]
                    del self.sleeping_tasklets[0]
                    # We have to send something, but it doesn't matter
                    # what as it is not used.
                    channel.send(None)
                    if self.has_sleeping_tasklets():
                        end_time = self.sleeping_tasklets[0][0]  # check next
                self.sleeping_ticks += 1
                stackless.schedule()
            self._run_tasklet.kill()
            self.running = False
            print('no more sleeping tasklets')

        def ensure_running(self):
            if self.running is False:
                self.running = True
                self._run_tasklet = stackless.tasklet(self._run)()

        def has_sleeping_tasklets(self):
            return len(self.sleeping_tasklets) > 0

        def sleep(self, secs):
            self.ensure_running()
            # next_sleep_id to disambiguate identical end_times in sorting
            self.next_sleep_id += 1
            channel = stackless.channel()
            end_time = self.sleeping_ticks + secs
            self.sleeping_tasklets.append((end_time, self.next_sleep_id, channel))
            self.sleeping_tasklets.sort()
            # Block until we get sent an awakening notification.
            channel.receive()

    sleeping_tasklet_mgr = SleepingTaskletManager()

    class StacklessChannel(stackless.channel):
        def send(self, value):
            with as_deadlock(RuntimeError):
                return stackless.channel.send(self, value)

        def receive(self):
            with as_deadlock(RuntimeError):
                return stackless.channel.receive(self)

    class StacklessBackend(Backend):
        def shortname(self):
            return 'stackless'

        def start(self, func, *args, **kwargs):
            return stackless.tasklet(func)(*args, **kwargs)

        def run(self, func, *args, **kwargs):
            t = self.start(func, *args, **kwargs)
            t.run()
            return t

        def channel(self):
            return StacklessChannel()

        def yield_(self):
            try:
                return stackless.schedule()
            except RuntimeError as ex:
                if ex.args[0] != 'No runnable tasklets left.':
                    print('no run')
                    pass
                raise

        def sleep(self, secs):
            try:
                sleeping_tasklet_mgr.sleep(secs)
                print('coop slept')
            except RuntimeError as ex:
                print('errored')
                if ex.args[0] == 'Deadlock: the last runnable tasklet cannot be blocked.':
                    _time.sleep(secs)
                else:
                    raise

        def resume(self, tasklet):
            tasklet.run()

        def propagate_exc(self, errtype, *args):
            stackless.getmain().throw(errtype, *args)

        def would_deadlock(self):
            if hasattr(stackless, 'runcount'):
                return stackless.runcount == 1
            return stackless.getruncount()

    return StacklessBackend()


def _make_gevent():
    import gevent
    import gevent.hub
    import gevent.queue
    import greenlet
    
    # We're importing socket to handle an known error in libev on Windows
    # See rgalanakis/goless#28 and surfly/gevent#459
    import socket

    deadlock_errtypes = (gevent.hub.LoopExit,)
    if _os.name == 'nt':
        deadlock_errtypes += (SystemError,)

    class Channel(gevent.queue.Channel):
        def send(self, value):
            with as_deadlock(deadlock_errtypes):
                self.put(value)

        def receive(self):
            with as_deadlock(deadlock_errtypes):
                return self.get()

    class GeventBackend(Backend):
        def shortname(self):
            return 'gevent'  # pragma: no cover

        def start(self, func, *args, **kwargs):
            grnlet = gevent.spawn(func, *args, **kwargs)
            return grnlet

        def run(self, func, *args, **kwargs):
            grnlet = self.start(func, *args, **kwargs)
            self.yield_()
            return grnlet

        def channel(self):
            return Channel()

        def yield_(self):
            with as_deadlock(gevent.hub.LoopExit):
                gevent.sleep()

        def sleep(self, secs):
            gevent.sleep(secs)

        def resume(self, tasklet):
            self.yield_()

        def propagate_exc(self, errtype, *args):
            raise errtype

        def would_deadlock(self):
            # The Hub and main greenlet are always running,
            # if there are more than those alive, we aren't going to deadlock.
            count = 0
            for obj in _gc.get_objects():
                if isinstance(obj, greenlet.greenlet) and not obj.dead:
                    count += 1
                    if count > 2:
                        return False
            return True

    return GeventBackend()


NO_VALID_BACKEND_MSG = """No valid backend could be created.
Valid backends are
gevent (for CPython, Stackless Python, or PyPy with newer version of gevent)
and stackless (for Stackless Python or PyPy).
You are currently running %s.
See goless.backends.calculate_backend for more details about what backend
is chosen under what conditions.""" % _sys.executable


class NoValidBackend(Exception):
    def __init__(self):
        Exception.__init__(self, NO_VALID_BACKEND_MSG)


class NullBackend(Backend):
    """Backend that raises a NoValidBackend when it is accessed or called.
    This allows goless to be imported, but not used,
    when no backend can be found.
    """

    def __getattribute__(self, item):
        raise NoValidBackend()

    def __call__(self, *args, **kwargs):
        raise NoValidBackend()


_default_backends = {
    'stackless': _make_stackless,
    'gevent': _make_gevent
}

is_pypy = _platform.python_implementation() == 'PyPy'


def _calc_default(backends):
    try:
        if is_pypy and 'gevent' in backends:
            return backends['gevent']()
        if 'stackless' in backends:
            return backends['stackless']()
    except ImportError:
        pass
    raise SystemError('Swallow this, please.')


def calculate_backend(name_from_env, backends=None):
    """
    Calculates which backend to use with the following algorithm:

    - Try to read the GOLESS_BACKEND environment variable.
      Usually 'gevent' or 'stackless'.
      If a value is set but no backend is available or it fails to be created,
      this function will error.
    - Determine the default backend (gevent for PyPy, stackless for Python).
      If no default can be determined or created, continue.
    - Try to create all the runtimes and choose the first one to create
      successfully.
    - If no runtime can be created, return a NullBackend,
      which will error when accessed.

    The "default" backend is the less-easy backend for a runtime.
    Since PyPy has stackless by default, gevent is intentional.
    Since Stackless is a separate interpreter for CPython,
    that is more intentional than gevent.
    We feel this is a good default behavior.
    """
    if backends is None:
        backends = _default_backends
    if name_from_env:
        if name_from_env not in backends:
            raise RuntimeError(
                'Invalid backend %r specified. Valid backends are: %s'
                % (name_from_env, _default_backends.keys()))
        # Allow this to raise, since it was explicitly set from the environment
        # noinspection PyCallingNonCallable
        return backends[name_from_env]()
    try:
        return _calc_default(backends)
    except SystemError:
        pass
    for maker in backends.values():
        # noinspection PyBroadException
        try:
            return maker()
        except Exception:
            pass
    return NullBackend()


current = calculate_backend(_os.getenv('GOLESS_BACKEND', ''))
