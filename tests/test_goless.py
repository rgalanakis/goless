import mock
import sys

import goless
from goless.backends import current as be
from . import BaseTests


class GoTests(BaseTests):

    def setUp(self):
        BaseTests.setUp(self)

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

    def test_starts_with_params(self):
        called = mock.Mock()
        goless.go(called, 10, a=1)
        be.yield_()
        called.assert_called_once_with(10, a=1)

    def test_exc(self):
        def raiseit():
            raise RuntimeError('ha!')
        goless.go(raiseit)
        be.yield_()
        self.assertEqual(len(self.panic_calls), 1)


class PanicTests(BaseTests):
    def test_panic_logs_and_exits(self):
        try:
            assert False
        except AssertionError:
            args = sys.exc_info()

        with mock.patch('logging.critical') as logmock:
            with self.assertRaises(SystemExit):
                goless.on_panic(*args)
        self.assertEqual(logmock.call_count, 1)
