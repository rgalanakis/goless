import mock

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

    def test_no_backends_raises(self):
        with self.assertRaises(RuntimeError):
            self.calc('', {})

    def test_default_backend_error_uses_fallback(self):
        # Regression test for found bug.
        testerbackends = dict(test_backends)

        def raiseit():
            raise ImportError('ho ho ho')
        testerbackends['gevent'] = raiseit
        self.assertEqual(self.calc('', testerbackends, ispypy=True), 'be_S')

    def test_no_valid_backends_raises(self):
        def raiseit():
            raise KeyError()

        with self.assertRaises(RuntimeError):
            self.calc('', {'a': raiseit})

    def test_default_shortname(self):
        class BE(backends.Backend):
            pass

        self.assertEqual(BE().shortname(), 'BE')
