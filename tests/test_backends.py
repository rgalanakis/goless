import mock
import traceback

from . import BaseTests
from goless import backends


test_backends = dict(
    stackless=lambda: 'be_S',
    gevent=lambda: 'be_G',
)


class CalcBackendTests(BaseTests):
    def calc(self, name, testbackends=test_backends, ispypy=False):
        with mock.patch('goless.backends.is_pypy', ispypy):
            return backends.calculate_backend(name, testbackends)

    def test_envvar_chooses_backend(self):
        be = self.calc('gevent')
        self.assertEqual(be, 'be_G')

    def test_invalid_envvar_raises(self):
        with self.assertRaises(RuntimeError):
            self.calc('invalid')

    def test_stackless_is_cpython_default(self):
        self.assertEqual(self.calc(''), 'be_S')

    def test_gevent_is_pypy_default(self):
        self.assertEqual(self.calc('', ispypy=True), 'be_G')

    def test_no_backends_uses_nullbackend(self):
        self.assertIsInstance(self.calc('', {}), backends.NullBackend)

    def test_default_backend_error_uses_fallback(self):
        # Regression test for found bug.
        testerbackends = dict(test_backends)

        def raiseit():
            raise ImportError('ho ho ho')
        testerbackends['gevent'] = raiseit
        self.assertEqual(self.calc('', testerbackends, ispypy=True), 'be_S')

    def test_no_valid_backends_uses_nullbackend(self):
        def raiseit():
            raise KeyError()

        self.assertIsInstance(
            self.calc('', {'a': raiseit}), backends.NullBackend)

    def test_default_shortname(self):
        class BE(backends.Backend):
            pass

        self.assertEqual(BE().shortname(), 'BE')


class NullBackendTests(BaseTests):
    def test_raises_on_access(self):
        nb = backends.NullBackend()
        with self.assertRaises(backends.NoValidBackend):
            nb.shortname()
        with self.assertRaises(backends.NoValidBackend):
            nb()

    def test_novalidbackend_msg(self):
        try:
            backends.NullBackend().shortname()
            self.fail('Should have raised!')
        except backends.NoValidBackend as ex:
            self.assertEqual(ex.args, (backends.NO_VALID_BACKEND_MSG,))


class CurrentBackendTests(BaseTests):
    """
    Tests that ensure the active backend adheres to its contract.
    Would need to be run for every backend for full coverage.
    """

    def testRecvWithNoWaitersRaisesDeadlock(self):
        with self.assertRaises(backends.Deadlock):
            backends.current.channel().receive()

    def testSendWithNoWaitersRaisesDeadlock(self):
        with self.assertRaises(backends.Deadlock):
            backends.current.channel().send(1)

    def testYieldNoWaitersDoesNotRaiseDeadlock(self):
        backends.current.yield_()

    def testChanOpsRaisesDeadlock(self):
        c = backends.current.channel()
        with self.assertRaises(backends.Deadlock):
            c.send(1)
        with self.assertRaises(backends.Deadlock):
            c.receive()


class AsDeadlockTests(BaseTests):
    def testReraises(self):
        try:
            with backends.as_deadlock(KeyError):
                raise KeyError()
            self.fail('Should have raised.')  # pragma: no cover
        except backends.Deadlock:
            raiseline = traceback.format_exc().splitlines()[-2]
            self.assertIn('raise KeyError()', raiseline)
