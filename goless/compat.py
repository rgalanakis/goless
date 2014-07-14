import sys

PY3 = sys.version_info[0] == 3

if PY3:
    # noinspection PyShadowingBuiltins
    range = range
    maxint = sys.maxsize

    # noinspection PyUnusedLocal
    def reraise(e, v, origex):
        raise e(v).with_traceback(origex.__traceback__)
else:
    # noinspection PyShadowingBuiltins
    range = xrange
    maxint = sys.maxint
    exec("""def reraise(e, v, origex):
    tb = sys.exc_info()[2]
    raise e, v, tb""")
