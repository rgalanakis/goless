import unittest

import goless
from . import run_tasklet


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
        run_tasklet(sendall)
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
        run_tasklet(recvall)
        self.assertEqual(markers, [])
        chan.send(1)
        self.assertEqual(markers, [1])
        chan.send(2)
        self.assertEqual(markers, [1, 2])

    def test_send_on_closed_chan_will_raise(self):
        chan = goless.chan(1)
        chan.send()
        chan.close()
        self.assertRaises(goless.ChannelClosed, chan.send)

    def test_recv_on_closed_chan_raises_after_chan_empties(self):
        chan = goless.chan(1)
        chan.send('hi')
        chan.close()
        self.assertEqual(chan.recv(), 'hi')
        self.assertRaises(goless.ChannelClosed, chan.recv)

    def test_range_with_closed_channel(self):
        chan = goless.chan(2)
        chan.send(1)
        chan.send(2)
        chan.close()
        items = [o for o in chan]
        self.assertEqual(items, [1, 2])

    def test_range_with_open_channel_blocks(self):
        pass