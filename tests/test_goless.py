import stackless
import unittest

import goless


class GoTests(unittest.TestCase):

    def setUp(self):
        # Make sure unhandled exceptions are observed in the context
        # of a single test.
        stackless.schedule()

        oldpanic = goless.on_panic
        self.panic_calls = []
        goless.on_panic = lambda *a: self.panic_calls.append(a)

        def restore_panic():
            goless.on_panic = oldpanic
        self.addCleanup(restore_panic)

        self.addCleanup(stackless.schedule)

    def test_starts_stuff(self):
        items = []
        goless.go(lambda: items.append(1))
        stackless.schedule()
        self.assertEqual(items, [1])

    def test_exc(self):
        def raiseit():
            raise RuntimeError('ha!')
        goless.go(raiseit)
        stackless.schedule()
        self.assertEqual(len(self.panic_calls), 1)
