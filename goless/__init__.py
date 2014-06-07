"""
``goless`` introduces go-like channels and select to Python,
built on top of Stackless Python (and maybe one day gevent).
Use :func:`goless.chan` to create a synchronous or buffered channel.
Use :func:`goless.select` like you would the ``Select`` function in Go's reflect package
(since Python lacks a switch/case statement, replicating Go's select statement syntax
wasn't very effective).
"""

import logging
import sys
import traceback

from .backends import current as _be


version_info = 0, 0, 1
version = '.'.join([str(v) for v in version_info])


def on_panic(etype, value, tb):
    """
    Called when there is an unhandled error in a goroutine.
    By default, logs and exits the process.
    """
    logging.critical(traceback.format_exception(etype, value, tb))
    _be.propagate_exc(SystemExit, 1)


def go(func, *args, **kwargs):
    """
    Run a function in a new tasklet, like a goroutine.
    If the goroutine raises an unhandled exception (*panics*),
    the :func:`goless.on_panic` will be called,
    which by default logs the error and exits the process.

    :param args: Positional arguments to ``func``.
    :param kwargs: Keyword arguments to ``func``.
    """
    def safe_wrapped(f):
        # noinspection PyBroadException
        try:
            f(*args, **kwargs)
        except:
            on_panic(*sys.exc_info())
    _be.start(safe_wrapped, func)
