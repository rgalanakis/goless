from __future__ import print_function

import sys
import time

from goless import backends, chan, go, selecting


QUEUE_LEN = 10000
CHANSIZE_AND_NAMES = (
    (0, 'Sync'),
    (-1, 'Async'),
    (1000, 'Buffered(1000)')
)

FILE = sys.stdout


def report(s, *args):
    print(s % args, file=FILE)


def bench_channel(chan_size):
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
    return end - start


def bench_channels():
    report('  Channels:')
    for size, name in CHANSIZE_AND_NAMES:
        took = bench_channel(size)
        report('    %s: %ss', name, took)


def bench_select(use_default):
    c = chan(0)
    cases = [
        selecting.scase(c, 1),
        selecting.rcase(c),
        selecting.scase(c, 1),
        selecting.rcase(c),
    ]
    if use_default:
        cases.append(selecting.dcase())

    def sender():
        while True:
            c.send(0)
            c.recv()
    go(sender)

    start = time.clock()
    for i in xrange(QUEUE_LEN):
        selecting.select(cases)
    end = time.clock()
    return end - start


def bench_selects():
    report('  Select:')
    took_nodefault = bench_select(False)
    report('    No default: %ss', took_nodefault)
    took_withdefault = bench_select(True)
    report('    With default: %ss', took_withdefault)


def main():
    global FILE
    if len(sys.argv) > 1:
        FILE = open(sys.argv[1], 'w')
    report('Benchmarking with backend %s:',
           backends.current.__class__.__name__)
    bench_channels()
    bench_selects()


if __name__ == '__main__':
    main()
