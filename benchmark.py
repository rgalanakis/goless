from __future__ import print_function

import time

from goless import chan, go, backends


QUEUE_LEN = 10000
CHANSIZE_AND_NAMES = (
    (0, 'Sync'),
    (-1, 'Async'),
    (1000, 'Buffered(1000)')
)


def _bench_channel(chan_size):
    c = chan(chan_size)

    def func():
        for _ in xrange(QUEUE_LEN):
            c.send(0)
        c.close()
    count = 0

    go(func)
    start = time.clock()
    for _ in xrange(QUEUE_LEN):
        c.recv()
        count += 1
    end = time.clock()
    assert count == QUEUE_LEN, '%s != %s' % (count, QUEUE_LEN)
    return end - start


if __name__ == '__main__':
    print('Using backend %s' % backends.current.__class__.__name__)
    print('Benchmarking channels:')
    for size, name in CHANSIZE_AND_NAMES:
        took = _bench_channel(size)
        print ('  %s: %s' % (took, name))
