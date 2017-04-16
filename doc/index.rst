goless: Go-style Python
=======================

- :ref:`a-intro`
- :ref:`a-goroutines`
- :ref:`a-channels`
- :ref:`a-select`
- :ref:`a-exceptions`
- :ref:`a-examples`
- :ref:`a-benchmarks`
- :ref:`a-backends`
- :ref:`a-compat`
- :ref:`a-gil`
- :ref:`a-references`
- :ref:`a-contrib`
- :ref:`a-misc`
- :ref:`a-tables`

.. _a-intro:

Intro
=====

The `goless library`_ provides **Go** programming language
semantics built on top of gevent_, `PyPy`_, or `Stackless Python`_.

For an example of what **goless** can do,
here is the Go program at https://gobyexample.com/select
reimplemented with **goless**::

    from goless import *
    
    c1 = chan()
    c2 = chan()

    def func1():
        time.sleep(1)
        c1.send('one')
    go(func1)

    def func2():
        time.sleep(2)
        c2.send('two')
    go(func2)

    for i in range(2):
        case, val = select(rcase(c1), rcase(c2))
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

The select function
===================

Go's ``select`` statement is implemented through the :func:`goless.select` function.
Because Python lacks anonymous blocks (*multiline lambdas*),
:func:`goless.select` works like Go's `reflect.Select`_ function.
Callers should create any number of :class:`goless.case` classes
that are passed into :func:`goless.select`.
The function returns the chosen case, which the caller will usually switch off of.
For example::

    from goless import *
    
    chan = chan()
    cases = [rcase(chan), scase(chan, 1), dcase()]
    chosen, value = select(cases)
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

The ``examples/`` folder contains a number of examples.

In addtion,
there are many examples from http://gobyexample.com implemented
via ``goless`` in the ``tests/test_examples.py`` file.

If there is an example you'd like to see,
or an idiomatic Go example you'd like converted,
please see :ref:`a-contrib` below.

.. _a-benchmarks:

Benchmarks
==========

You can run benchmarks using the current Python interpreter and configured
backend by running the following from the ``goless`` project directory::

    $ python -m benchmark

Developers may run benchmarks locally and report them into the following table.
The **Go** versions of the benchmarks are also run.
The numbers are useful for relative comparisons only:

.. include:: benchtable.rst

To regenerate this table, run::

    $ python write_benchmarks.py

To print the table to stdout, run (notice the trailing ``-`` char)::

    $ python write_benchresults.py -

Assuming you have **Go** installed, you can run the benchmarks with::

    $ go run benchmark.go

.. _a-backends:

Backends
========

There are two backends for concurrently available in
:mod:`goless.backends`.
Backends should only be used by ``goless``,
and not by any client code.
You can choose between backends by setting the environment variable
``GOLESS_BACKEND`` to ``"gevent"`` or ``"stackless"``.
Otherwise, an appropriate backend will be chosen.
If neither ``gevent`` or ``stackless`` are available,
``goless`` will raise an error when used (but will still be importable).

.. _a-compat:

Compatibility Details
=====================

The good news is that you probably don't need to worry about any of this,
and goless works almost everywhere.

The bad news is, almost all abstractions are leaky,
and there can be some nuances to compatibility.
If you run into an issue where ``goless`` cannot create a backend,
you may need to read the following sections.

.. _a-pypy:

PyPy
----

``goless`` works under PyPy out of the box with the stackless
backend, because PyPy includes a ``stackless.py`` file in its standard library.
This appears to work properly, but fails the ``goless`` test suite.
We are not sure why yet, as ``stackless.py`` does not have a real maintainer
and the bug is difficult to track down.
However, the examples and common usages seem to all work fine.

Using PyPy 2.2+ and the tip of gevent's GitHub repo
( https://github.com/surfly/gevent ),
the gevent backend works and is fully tested.

Python 2 (CPython)
------------------

Using Python 2 and the CPython interpreter,
you can use the gevent backend for ``goless``
with no problems.
Under Python 2, you can just do::

    $ pip install gevent
    $ pip install goless

Python 3 (CPython)
------------------

Newer versions of gevent include Python 3 compatibility.
To install gevent on Python3, you also **must** install Cython.
So you can use thew following commands to install ``goless``
under Python3 with its gevent backend::

    $ pip install cython
    $ pip install git+https://github.com/surfly/gevent.git#gevent-egg
    $ pip install goless

This works and is tested.

Stackless Python
----------------

All versions of Stackless Python (2 and 3) should work with goless.
However, we cannot test with Stackless Python on Travis,
so we only test with it locally.
If you find any problems, *please* report an issue.

.. _a-gil:

goless and the GIL
==================

``goless`` does not address CPython's **Global Interpreter Lock** (**GIL**) at all.
``goless`` does not magically provide any parallelization.
It provides Go-like semantics, but not its performance.
Perhaps this will change in the future if the GIL is removed.
Another option is PyPy's STM branch,
which ``goless`` will (probably) benefit heartily.

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
- PyPy: http://pypy.org/
- Idiomatic Go Examples: http://gobyexample.com

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

.. _a-tables:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _reflect.Select: http://golang.org/pkg/reflect/#Select
.. _goless library: https://github.com/rgalanakis/goless
.. _Stackless Python: http://www.stackless.com/
.. _gevent: http://www.gevent.org/
.. _PyPy: http://pypy.org/