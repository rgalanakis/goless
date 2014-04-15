import stackless
import stacklesslib.util as sutil
import unittest

import goless
from goless import debug


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
        self.ca = goless.rcase(self.ch, lambda x: x * 2)

    def test_ready(self):
        self.assertFalse(self.ca.ready())
        sutil.tasklet_run(self.ch.send, [1])
        self.assertTrue(self.ca.ready())
        sutil.tasklet_run(self.ch.recv)
        self.assertFalse(self.ca.ready())

    def test_executes(self):
        sutil.tasklet_run(self.ch.send, 'a')
        x = self.ca.exec_()
        self.assertEqual(x, 'aa')

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
        self.side_effect = []
        self.sendval = 1
        self.sideffect_val = 2
        self.ca = goless.scase(
            self.ch,
            self.sendval,
            lambda: self.side_effect.append(self.sideffect_val))

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
        self.assertEqual(self.side_effect, [self.sideffect_val])
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
        chan1 = goless.chan()
        result = goless.select(
            goless.rcase(chan1, raiseit),
            default=lambda: 7
        )
        self.assertEqual(result, 7)

    def test_select_chooses_ready_selection(self):
        readychan = goless.chan(1)
        notreadychan = goless.chan(1)
        readychan.send(3)
        result = goless.select(
            goless.rcase(notreadychan, raiseit),
            goless.rcase(readychan, lambda x: x * 2),
            default=raiseit
        )
        self.assertEqual(result, 6)

    def test_select_no_default_no_ready_blocks(self):
        chan1 = goless.chan()
        chan2 = goless.chan()
        a = []

        def sel():
            a.append(goless.select(
                goless.rcase(chan2, lambda x: x),
                goless.rcase(chan1, lambda x: x),
            ))
        sutil.tasklet_new(sel)
        self.assertEqual(a, [])
        chan1.send(5)
        stackless.run(0)
        self.assertEqual(a, [5])

    def test_main_tasklet_can_select(self):
        chan1 = goless.chan(1)

        goless.select(
            goless.scase(chan1),
        )


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
            goless.select(
                goless.rcase(c1, callbacks.append),
                goless.rcase(c2, callbacks.append),
            )

        self.assertEqual(callbacks, ['one', 'two'])
