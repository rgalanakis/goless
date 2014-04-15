import stacklesslib.util as sutil
import unittest

import goless


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
    def setUp(self):
        self.ch = goless.chan(1)
        self.ca = goless.rcase(self.ch, lambda x: x * 2)

    def test_ready(self):
        self.assertFalse(self.ca.ready())
        self.ch.send(1)
        self.assertTrue(self.ca.ready())
        self.ch.recv()
        self.assertFalse(self.ca.ready())

    def test_executes(self):
        self.ch.send('a')
        x = self.ca.exec_()
        self.assertEqual(x, 'aa')

    def test_exec_with_no_body(self):
        self.ch.send('a')
        ca = goless.rcase(self.ch)
        self.assertEqual(ca.exec_(), 'a')


class SendCaseTests(unittest.TestCase):
    def setUp(self):
        self.ch = goless.chan(1)
        self.side_effect = []
        self.sendval = 1
        self.sideffect_val = 2
        self.ca = goless.scase(
            self.ch,
            self.sendval,
            lambda: self.side_effect.append(self.sideffect_val))

    def test_ready(self):
        self.assertTrue(self.ca.ready())
        self.ch.send(None)
        self.assertFalse(self.ca.ready())
        sutil.tasklet_run(self.ch.recv)
        self.assertTrue(self.ca.ready())
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
        self.ca.exec_()


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
        chan1 = goless.chan(1)
        chan2 = goless.chan(1)
        a = []

        def sel():
            a.append(goless.select(
                goless.rcase(chan2),
                goless.rcase(chan1),
            ))
        sutil.tasklet_new(sel)
        self.assertEqual(a, [])  # Nothing is ready
        chan1.send(5)
        self.assertEqual(a, [5])
