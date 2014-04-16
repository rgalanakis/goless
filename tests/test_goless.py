import unittest

import goless
from goless.backends import stackless_backend as be


class GoTests(unittest.TestCase):

    def setUp(self):
        # Make sure unhandled exceptions are observed in the context
        # of a single test.
        be.yield_()

        oldpanic = goless.on_panic
        self.panic_calls = []
        goless.on_panic = lambda *a: self.panic_calls.append(a)

        def restore_panic():
            goless.on_panic = oldpanic
        self.addCleanup(restore_panic)

        self.addCleanup(be.yield_)

    def test_starts_stuff(self):
        items = []
        goless.go(lambda: items.append(1))
        be.yield_()
        self.assertEqual(items, [1])

    def test_exc(self):
        def raiseit():
            raise RuntimeError('ha!')
        goless.go(raiseit)
        be.yield_()
        self.assertEqual(len(self.panic_calls), 1)
