import unittest

from goless.backends import current as be


class BaseTests(unittest.TestCase):

    def setUp(self):
        be.yield_()
        def doYield():
            be.yield_()
        self.addCleanup(doYield)
