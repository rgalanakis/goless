"""
This file demonstrates how to implement futures or promises
with goless.
Futures are useful when you will *eventually* need the result of some
operation, and can compute it (or start computing it) before you actually
need the value.

The following code provides a math API for inverting and multiplying numbers.
Each function provides a synchronous version (inverse),
and asynchronous version (inverse_async).
The asynchronous versions use futures,
and the synchronous versions just use the async versions but immediately
'cash in' the future.

The 'main' function multiplies the inverses of two terms.
It first does this by using the synchronous versions of inverse and product.
After that, it does it with the async versions.
The inverse calls are set up in parallel and only run when or before they
are actually requested.

See http://www.golangpatterns.info/concurrency/futures
for more information.
"""
from __future__ import print_function

import goless


# First create the async versions built on promises
def inverse_async(future):
    c = goless.chan()
    goless.go(lambda: c.send(future.recv() * -1))
    return c


def product_async(future_a, future_b):
    c = goless.chan()
    goless.go(lambda: c.send(future_a.recv() * future_b.recv()))
    return c


# And implement synchronous versions in terms of the async versions.
# Use the promise helper to create a future.
def inverse(a):
    return inverse_async(promise(a)).recv()


def product(a, b):
    return product_async(promise(a), promise(b)).recv()


def promise(value):
    future = goless.chan(1)
    future.send(value)
    return future


def main():
    a, b = 2, -4

    def inverse_product_sync():
        ai = inverse(a)
        bi = inverse(b)
        return product(ai, bi)

    def inverse_product_async():
        ai_future = inverse_async(promise(a))
        bi_future = inverse_async(promise(b))
        return product_async(ai_future, bi_future)

    print('Sync: %s' % inverse_product_sync())
    print('Async: %s' % inverse_product_async().recv())


if __name__ == '__main__':
    main()
