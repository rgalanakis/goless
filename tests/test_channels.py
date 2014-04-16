import unittest

import goless
import goless.channels as gochans
from . import run_tasklet


class ChanTests(unittest.TestCase):
    def test_return_types(self):
        self.assertIsInstance(gochans.chan(0), gochans.SyncChannel)
        self.assertIsInstance(gochans.chan(None), gochans.SyncChannel)
        self.assertIsInstance(gochans.chan(-1), gochans.AsyncChannel)
        self.assertIsInstance(gochans.chan(1), gochans.BufferedChannel)


class SyncChannelTests(unittest.TestCase):
    def test_behavior(self):
        chan = gochans.SyncChannel()
        results = []

        goless.go(lambda: chan.send(1))

        def check_results_empty():
            self.assertFalse(results)
            chan.send(2)
        goless.go(check_results_empty)

        results = [chan.recv(), chan.recv()]
        self.assertEqual(results, [1, 2])


class AsyncChannelTests(unittest.TestCase):
    def test_behavior(self):
        # Obviously we cannot test an infinite buffer,
        # but we can just test a huge one's behavior.
        chan = gochans.AsyncChannel()
        for _ in xrange(10000):
            chan.send()
        chan.close()
        for _ in chan:
            pass


class BufferedChannelTests(unittest.TestCase):
    def test_size_must_be_valid(self):
        for size in 0, -1, '', None:
            self.assertRaises(AssertionError, gochans.BufferedChannel, size)

    def test_behavior(self):
        resultschan = gochans.BufferedChannel(5)
        endchan = gochans.SyncChannel()

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
        chan = gochans.BufferedChannel(2)
        markers = []

        def sendall():
            markers.append(chan.send(4))
            markers.append(chan.send(3))
            markers.append(chan.send(2))
            markers.append(chan.send(1))
        run_tasklet(sendall)
        self.assertEqual(len(markers), 2)
        got = [chan.recv(), chan.recv()]
        self.assertEqual(len(markers), 4)
        self.assertEqual(got, [4, 3])
        got.extend([chan.recv(), chan.recv()])
        self.assertEqual(got, [4, 3, 2, 1])

    def test_buffered_chan_will_block_on_recv_with_no_items(self):
        chan = gochans.BufferedChannel(1)
        markers = []

        def recvall():
            markers.append(chan.recv())
            markers.append(chan.recv())
        run_tasklet(recvall)
        self.assertEqual(markers, [])
        chan.send(1)
        self.assertEqual(markers, [1])
        chan.send(2)
        self.assertEqual(markers, [1, 2])

    def test_send_on_closed_chan_will_raise(self):
        chan = gochans.BufferedChannel(1)
        chan.send()
        chan.close()
        self.assertRaises(gochans.ChannelClosed, chan.send)

    def test_recv_on_closed_chan_raises_after_chan_empties(self):
        chan = gochans.BufferedChannel(1)
        chan.send('hi')
        chan.close()
        self.assertEqual(chan.recv(), 'hi')
        self.assertRaises(gochans.ChannelClosed, chan.recv)

    def test_range_with_closed_channel(self):
        chan = gochans.BufferedChannel(2)
        chan.send(1)
        chan.send(2)
        chan.close()
        items = [o for o in chan]
        self.assertEqual(items, [1, 2])

    def test_range_with_open_channel_blocks(self):
        pass