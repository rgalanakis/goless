"""
This file demonstrates a parallel for loop using goless.
The parallel for pattern is very simple,
so I chose a simple example (negating an integer),
rather than something more realistic.

The example uses shared memory and a 'semaphor' channel.
Shared memory is normally a no-no,
but is useful here so we don't need the overhead of using
extra channels.

See http://www.golangpatterns.info/concurrency/parallel-for-loop
for more information.
"""

from __future__ import print_function

import goless


def dosomething(x):
    return x * -1


def pfor():
    n = 10
    items = xrange(n)
    results = [None] * n
    semaphore = goless.chan(n)

    def mapper(index, value):
        results[index] = dosomething(value)
        semaphore.send()

    for i, item in enumerate(items):
        mapper(i, item)
    for _ in xrange(n):
        semaphore.recv()
    print('Finished: %s' % results)


if __name__ == '__main__':
    pfor()
