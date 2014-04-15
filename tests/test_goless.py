import stackless
import stacklesslib.util as sutil
import unittest

import goless
from goless.debug import debug


def raiseit(*args, **kwargs):
    raise AssertionError('Should not see this: args: %s kwargs: %s' % (args, kwargs))


class ChanTests(unittest.TestCase):
    def test_unbuffered_chan(self):
        chan = goless.chan()
        results = []

        goless.go(lambda: chan.send(1))

        def check_results_empty():
            self.assertFalse(results)
            chan.send(2)
        goless.go(check_results_empty)

        results = [chan.recv(), chan.recv()]
        self.assertEqual(results, [1, 2])

    def test_buffered_chan_will_buffer(self):
        resultschan = goless.chan(5)
        endchan = goless.chan()

        def square(x):
            return x * x

        def func():
            for num in range(5):
                resultschan.send(square(num))
            endchan.send()

        goless.go(func)
        # Waiting on the endchan tells us our results are
        # queued up in resultschan
        endchan.recv()
        got = [resultschan.recv() for _ in range(5)]
        ideal = [square(i) for i in range(5)]
        self.assertEqual(got, ideal)

    def test_buffered_chan_will_block_at_max_size(self):
        chan = goless.chan(2)
        markers = []

        def sendall():
            markers.append(chan.send(4))
            markers.append(chan.send(3))
            markers.append(chan.send(2))
            markers.append(chan.send(1))
        sutil.tasklet_run(sendall)
        self.assertEqual(len(markers), 2)
        got = [chan.recv(), chan.recv()]
        self.assertEqual(len(markers), 4)
        self.assertEqual(got, [4, 3])
        got.extend([chan.recv(), chan.recv()])
        self.assertEqual(got, [4, 3, 2, 1])

    def test_buffered_chan_will_block_on_recv_with_no_items(self):
        chan = goless.chan(1)
        markers = []

        def recvall():
            markers.append(chan.recv())
            markers.append(chan.recv())
        sutil.tasklet_run(recvall)
        self.assertEqual(markers, [])
        chan.send(1)
        self.assertEqual(markers, [1])
        chan.send(2)
        self.assertEqual(markers, [1, 2])


class RecvCaseTests(unittest.TestCase):
    chansize = 1

    def setUp(self):
        self.ch = goless.chan(self.chansize)
        self.ca = goless.rcase(self.ch)

    def test_ready(self):
        self.assertFalse(self.ca.ready())
        sutil.tasklet_run(self.ch.send, [1])
        self.assertTrue(self.ca.ready())
        sutil.tasklet_run(self.ch.recv)
        self.assertFalse(self.ca.ready())

    def test_executes(self):
        sutil.tasklet_run(self.ch.send, 'a')
        x = self.ca.exec_()
        self.assertEqual(x, 'a')

    def test_exec_with_no_body(self):
        sutil.tasklet_run(self.ch.send, ['a'])
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
        sutil.tasklet_run(self.ch.send)
        self.assertFalse(self.ca.ready())
        sutil.tasklet_run(self.ch.recv)
        assert_default_readiness()
        sutil.tasklet_run(self.ch.send)
        self.assertFalse(self.ca.ready())

    def test_executes(self):
        def recv():
            a.append(self.ch.recv())
        a = []
        sutil.tasklet_run(recv)
        self.ca.exec_()
        self.assertEqual(a, [self.sendval])

    def test_exec_no_onselected(self):
        sutil.tasklet_run(self.ch.recv)
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
        sutil.tasklet_new(sel)
        self.assertEqual(a, [])
        chan1.send(5)
        stackless.run(0)
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


import time


class Examples(unittest.TestCase):

    def test_select(self):
        # https://gobyexample.com/select
        c1 = goless.chan()
        c2 = goless.chan()

        def func1():
            time.sleep(.1)
            debug('sending1')
            c1.send('one')
            debug('sent1')
        goless.go(func1)

        def func2():
            time.sleep(.2)
            debug('sending2')
            c2.send('two')
            debug('sent2')
        goless.go(func2)

        # We don't print since we run this as a test.
        callbacks = []

        for i in range(2):
            debug('loop %s', i)
            _, val = goless.select([goless.rcase(c1), goless.rcase(c2)])
            callbacks.append(val)

        self.assertEqual(callbacks, ['one', 'two'])
