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

# noinspection PyUnresolvedReferences
from .channels import chan, ChannelClosed
# noinspection PyUnresolvedReferences
from .selecting import dcase, rcase, scase, select


version_info = 0, 5, 0
version = '.'.join([str(v) for v in version_info])

__version__ = version
__author__ = 'Rob Galanakis'
__email__ = 'rob.galanakis@gmail.com'
__url__ = 'https://github.com/rgalanakis/goless'
__license__ = 'Apache'


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
