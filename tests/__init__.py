import sys
try:
    # noinspection PyPackageRequirements
    import unittest2 as unittest
    sys.modules['unittest'] = unittest
except ImportError:
    import unittest

from goless.backends import current as be


class BaseTests(unittest.TestCase):
    """
    Base class for unit tests.
    Yields in setup and teardown so no lingering tasklets
    are run in a later test,
    potentially causing an error that would leave people scratching their heads.
    """

    def setUp(self):
        be.yield_()

        def doyield():
            be.yield_()
        self.addCleanup(doyield)
