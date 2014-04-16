"""
``goless`` introduces go-like channels and select to Python,
built on top of Stackless Python (and maybe one day gevent).
Use :func:`goless.chan` to create a synchronous or buffered channel.
Use :func:`goless.select` like you would the ``Select`` function in Go's reflect package
(since Python lacks a switch/case statement, replicating Go's select statement syntax
wasn't very effective).
"""

import logging
import stackless as _stackless
import sys
import traceback

from .channels import chan, ChannelClosed
from .select import dcase, rcase, scase, select


version_info = 0, 0, 1
version = '.'.join([str(v) for v in version_info])


def on_panic(etype, value, tb):
    """
    Called when there is an unhandled error in a goroutine.
    By default, logs and exits the process.
    """
    logging.critical(traceback.format_exception(etype, value, tb))
    _stackless.getmain().throw(SystemExit, 1)


def go(func):
    """
    Run a function in a new tasklet, like a goroutine.
    If the goroutine raises an unhandled exception (*panics*),
    the :func:`on_panic` will be called,
    which by default logs the error and exits the process.
    """
    def safe_wrapped(f):
        # noinspection PyBroadException
        try:
            f()
        except:
            on_panic(*sys.exc_info())
    _stackless.tasklet(safe_wrapped)(func)
