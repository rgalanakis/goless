"""``goless`` introduces go-like channels and select to Python,
built on top of Stackless Python (and maybe one day gevent).
Use :func:`goless.chan` to create a synchronous or buffered channel.
Use :func:`goless.select` like you would the ``Select`` function in Go's reflect package
(since Python lacks a switch/case statement, replicating Go's select statement syntax
wasn't very effective).
"""

import stackless as _stackless


from .channels import chan, ChannelClosed
from .select import dcase, rcase, scase, select


version_info = 0, 0, 1
version = '.'.join([str(v) for v in version_info])


def go(func):
    """Run a function in a new tasklet, like a goroutine."""
    _stackless.tasklet(func)()
