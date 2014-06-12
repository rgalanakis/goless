import sys

PY3 = sys.version_info[0] == 3

if PY3:
    # noinspection PyShadowingBuiltins
    range = range
    maxint = sys.maxsize
else:
    # noinspection PyShadowingBuiltins
    range = xrange
    maxint = sys.maxint
