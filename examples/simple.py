"""
A really simple example to use when demonstrating goless.
"""
from __future__ import print_function

import goless


def simple():
    channel = goless.chan()

    def goroutine():
        while True:
            value = channel.recv()
            channel.send(value ** 2)
    goless.go(goroutine)

    for i in range(2, 5):
        channel.send(i)
        squared = channel.recv()
        print('%s squared is %s' % (i, squared))

    # Output:
    # 2 squared is 4
    # 3 squared is 9
    # 4 squared is 16

if __name__ == '__main__':
    simple()
