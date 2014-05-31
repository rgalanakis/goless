from . import BaseTests
from goless import backends

test_backends = dict(
    a=lambda: 'be_A',
    b=lambda: 'be_B',
)


class CalcBackendTests(BaseTests):
    def calc(self, name, testbackends=test_backends):
        return backends.calculate_backend(name, testbackends)

    def test_valid_envvar_name(self):
        be = self.calc('a')
        self.assertEqual(be, 'be_A')

    def test_invalid_envvar_name(self):
        with self.assertRaises(RuntimeError):
            self.calc('invalid')

    def test_default(self):
        be = self.calc('')
        self.assertIn(be, [v() for v in test_backends.values()])

    def test_no_backends(self):
        with self.assertRaises(RuntimeError):
            self.calc('', {})

    def test_invalid_backends(self):
        def raiseit():
            raise KeyError()

        with self.assertRaises(RuntimeError):
            self.calc('', {'a': raiseit})
