.. _a-intro:

Intro
=====

The `goless library`_ provides **Go** programming language
semantics built on top of `Stackless Python`_ or gevent_.

For an example of what **goless** can do,
here is the Go program at https://gobyexample.com/select
reimplemented with **goless**::

    c1 = goless.chan()
    c2 = goless.chan()

    def func1():
        time.sleep(1)
        c1.send('one')
    goless.go(func1)

    def func2():
        time.sleep(2)
        c2.send('two')
    goless.go(func2)

    for i in range(2):
        case, val = goless.select([goless.rcase(c1), goless.rcase(c2)])
        print(val)

It is surely a testament to Go's style that it isn't much less Python code than Go code,
but I quite like this. Don't you?

.. _a-goroutines:

Goroutines
==========

The :func:`goless.go` function mimics Go's goroutines by, unsurprisingly,
running the routine in a tasklet/greenlet.
If an unhandled exception occurs in a goroutine, :func:`goless.on_panic` is called.

.. autofunction:: goless.go

.. autofunction:: goless.on_panic

.. _a-channels:

Channels
========

There are three types of channels available in ``goless``.
Use the :func:`goless.chan` function to create a channel.
The channel implementations contain more thorough documentation
about how they actually work.

.. autofunction:: goless.chan

.. autoclass:: goless.channels.GoChannel
    :members: send, recv, close

.. autoclass:: goless.ChannelClosed

.. _a-select:

The ``select`` function
=======================

Go's ``select`` statement is implemented through the :func:`goless.select` function.
Because Python lacks anonymous blocks (*multiline lambdas*),
:func:`goless.select` works like Go's `reflect.Select`_ function.
Callers should create any number of :class:`goless.case` classes
that are passed into :func:`goless.select`.
The function returns the chosen case, which the caller will usually switch off of.
For example::

    chan = goless.chan()
    cases = [goless.rcase(chan), goless.scase(chan, 1), goless.dcase()]
    chosen, value = goless.select(cases)
    if chosen is cases[0]:
        print('Received %s' % value)
    elif chosen is cases[1]:
        assert value is None
        print('Sent.')
    else:
        assert chosen is cases[2]
        print('Default...')

Callers should never have to do anything with cases,
other than create and switch off of them.

.. autofunction:: goless.select

.. autoclass:: goless.dcase

.. autoclass:: goless.rcase

.. autoclass:: goless.scase

.. _a-exceptions:

Exception Handling
==================

Exception handling is a tricky topic and may change in the future.
The default behavior right now is that an unhandled exception in a goroutine will
log the exception and take down the entire process.
This in theory emulates Go's ``panic`` behavior:
if a goroutine panics, the process will exit.

If you are not happy with this behavior,
you should patch `goless.on_panic` to provide custom behavior.

If you find a better pattern, create an issue on GitHub.

.. _a-examples:

Examples
========

There are many examples from http://gobyexample.com implemented
via ``goless``. See the ``tests/test_examples.py`` file.
If you have an idiomatic Go example you'd like converted,
please see :ref:`a-contrib` below.

.. _a-backends:

Backends
========

There are two backends for concurrently available in
:mod:`goless.backends`.
These backends should only be used by `goless`,
and not by any client code.
You can choose between backends by setting the environment variable
``GOLESS_BACKEND`` to ``"gevent"`` or ``"stackless"``.
Otherwise, an appropriate backend will be chosen,
preferring ``stackless`` first.
If neither ``gevent`` or ``stackless`` are available,
a ``RuntimeError`` is raised on ``goless`` import.

.. _a-pypy:

goless and PyPy
===============

``goless`` should work under PyPy with
both ``stackless`` and ``gevent`` backends.

PyPy includes a ``stackless.py`` module in its standard library,
which can be used to power ``goless``.
This appears to work properly, but fails the ``goless`` test suite.
We are not sure why yet, as ``stackless.py`` does not have a real maintainer
and the bug is difficult to track down.
However, the examples and common usages seem to all work fine.

New versions of ``gevent``
(not yet on PyPI, but in the surfly/gevent GitHub repository)
work great with newer versions of PyPy.

.. _a-references:

References
==========

- **goless** on GitHub: https://github.com/rgalanakis/goless
- **goless** on Read the Docs: http://goless.readthedocs.org/
- **goless** on Travis-CI: https://travis-ci.org/rgalanakis/goless
- **goless** on Coveralls: https://coveralls.io/r/rgalanakis/goless
- The Go Programming Language: http://www.golang.org
- Stackless Python: http://www.stackless.com
- gevent: http://gevent.org/
- Idiomatic Go Examples: http://gobyexample.com

.. toctree::
   :maxdepth: 2

.. _a-contrib:

Contributing
============

I am definitely not a Go expert,
so improvements to make things more idiomatic are very welcome.
Please create an issue or pull request on GitHub: https://github.com/rgalanakis/goless

``goless`` was created by a number of people  at the PyCon 2014 sprints.
Even a small library like ``goless`` is the product of lots of collaboration.

Maintainers:

- Rob Galanakis <rob.galanakis@gmail.com>
- Simon König <simjoko@gmail.com>
- Carlos Knippschild <carlos.chuim@gmail.com>

Special thanks:

- Kristján Valur Jónsson <sweskman@gmail.com>
- Andrew Francis <af.stackless@gmail.com>

.. _a-misc:

Miscellany
==========

Coverage is wrong. It should be higher.
The coverage module does not work properly with gevent and stackless.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _reflect.Select: http://golang.org/pkg/reflect/#Select
.. _goless library: https://github.com/rgalanakis/goless
.. _Stackless Python: http://www.stackless.com/
.. _gevent: http://www.gevent.org/
