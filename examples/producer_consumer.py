"""
This file demonstrates a simple producer/consumer setup.
The produce goroutine generates some data and sends on a channel,
and the consume goroutine receives on the channel and processes
the data.

This is one of the simplest models of concurrent programming
and very easy with goless.

Code modeled on http://www.golangpatterns.info/concurrency/producer-consumer.
"""
import sys

import goless


def main():
    done = goless.chan()
    msgs = goless.chan()
    out = goless.chan()

    def produce():
        for i in range(10):
            msgs.send(i)
        done.send()

    def consume(name):
        for msg in msgs:
            out.send('%s:%s ' % (name, msg))

    def logger():
        for msg in out:
            sys.stdout.write(msg)
        sys.stdout.write('\n')

    goless.go(produce)
    goless.go(consume, "one")
    goless.go(consume, "two")
    goless.go(logger)
    done.recv()


if __name__ == '__main__':
    main()
