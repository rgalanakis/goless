"""
This file demonstrates how to implement a coroutine in goless
using channels.
I would usually not suggest doing this (and using a Python generator instead),
but you may have a use for it.

See http://www.golangpatterns.info/concurrency/coroutines
for more info.
"""
from __future__ import print_function

import goless


def main():
    def integers():
        yielder = goless.chan()

        def counter():
            count = 0
            while True:
                yielder.send(count)
                count += 1

        goless.go(counter)
        return yielder

    resume = integers()

    def generate_integer():
        return resume.recv()

    print(generate_integer())
    print(generate_integer())
    print(generate_integer())


if __name__ == '__main__':
    main()
