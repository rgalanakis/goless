import stackless
import unittest

import goless
from goless.backends import stackless_backend as be


class RecvCaseTests(unittest.TestCase):
    chansize = 1

    def setUp(self):
        self.ch = goless.chan(self.chansize)
        self.ca = goless.rcase(self.ch)

    def test_ready(self):
        self.assertFalse(self.ca.ready())
        be.run(self.ch.send, 1)
        self.assertTrue(self.ca.ready())
        be.run(self.ch.recv)
        self.assertFalse(self.ca.ready())

    def test_executes(self):
        be.run(self.ch.send, 'a')
        x = self.ca.exec_()
        self.assertEqual(x, 'a')

    def test_exec_with_no_body(self):
        be.run(self.ch.send, 'a')
        ca = goless.rcase(self.ch)
        self.assertEqual(ca.exec_(), 'a')


class RecvCaseUnbufferedTests(RecvCaseTests):
    chansize = 0


class SendCaseTests(unittest.TestCase):
    chansize = 1

    def setUp(self):
        self.ch = goless.chan(self.chansize)
        self.sendval = 1
        self.ca = goless.scase(self.ch, self.sendval)

    def test_ready(self):
        def assert_default_readiness():
            self.assertEquals(self.ca.ready(), self.chansize > 0)

        assert_default_readiness()
        be.run(self.ch.send)
        self.assertFalse(self.ca.ready())
        be.run(self.ch.recv)
        assert_default_readiness()
        be.run(self.ch.send)
        self.assertFalse(self.ca.ready())

    def test_executes(self):
        def recv():
            a.append(self.ch.recv())
        a = []
        be.run(recv)
        self.ca.exec_()
        self.assertEqual(a, [self.sendval])

    def test_exec_no_onselected(self):
        be.run(self.ch.recv)
        self.ca.exec_()


class SendCaseUnbufferedTests(SendCaseTests):
    chansize = 0


class SelectTests(unittest.TestCase):
    def setUp(self):
        self.chan1 = goless.chan()

    def test_select_uses_default(self):
        cases = [goless.rcase(self.chan1), goless.dcase()]
        result, val = goless.select(cases)
        self.assertIs(result, cases[1])
        self.assertIsNone(val)

    def test_select_chooses_ready_selection(self):
        readychan = goless.chan(1)
        notreadychan = goless.chan(1)
        readychan.send(3)
        cases = [goless.rcase(notreadychan), goless.rcase(readychan), goless.dcase()]
        result, val = goless.select(cases)
        self.assertIs(result, cases[1])
        self.assertEqual(val, 3)

    def test_select_no_default_no_ready_blocks(self):
        chan1 = goless.chan()
        chan2 = goless.chan()
        a = []
        cases = [goless.rcase(chan2), goless.rcase(chan1)]

        def sel():
            a.append(goless.select(cases))
        be.run(sel)
        self.assertEqual(a, [])
        chan1.send(5)
        stackless.schedule()
        self.assertEqual(len(a), 1)
        chosen, val = a[0]
        self.assertEqual(chosen, cases[1])
        self.assertEqual(val, 5)

    def test_main_tasklet_can_select(self):
        chan1 = goless.chan(1)
        cases = [goless.scase(chan1, 3)]
        chosen, val = goless.select(cases)
        self.assertIs(chosen, cases[0])
        self.assertIsNone(val)
