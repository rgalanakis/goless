goless: Go-style Python
=======================

- :ref:`a-intro`
- :ref:`a-goroutines`
- :ref:`a-channels`
- :ref:`a-select`
- :ref:`a-exceptions`
- :ref:`a-examples`
- :ref:`a-backends`
- :ref:`a-references`
- :ref:`a-contrib`

.. _a-intro:

Intro
=====

The **goless** library provides **Go** programming language
semantics built on top of **Stackless Python** or **gevent**.

For example, the code at https://gobyexample.com/select
can be roughly implemented as follows::

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

goroutines
==========

The :func:`goless.go` function mimics Go's goroutines by, unsurprisingly,
running the routine in a tasklet/greenlet.
If an unhandled exception occurs in a goroutine, :func:`goless.on_panic` is called.

.. autofunction:: goless.go

.. autofunction:: goless.on_panic

.. _a-channels:

channels
========

There are three types of channels available in ``goless``.
Use the :func:`goless.chan` function to create a channel.
The channel implementations contain more thorough documentation
about how they actually work.

.. autofunction:: goless.chan

.. autoclass:: goless.channels.GoChannel
    :members: send, recv, close

.. _a-select:

The ``select`` function
=======================

Go's ``select`` statement is implemented through the :func:`goless.select` function.
Because Python lacks anonymous blocks (*multiline lambdas*),
:func:`goless.select` works like Go's ``reflect.Select`` function.

.. autofunction:: goless.select

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
More idiomatic examples are encouraged.

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

.. _a-references:

References
==========

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

``goless`` was created by a number of people  at the PyCon 2014 sprints.
Even a small library like ``goless`` is the product of lots of collaboration.

Maintainers:

- Rob Galanakis <rob.galanakis@gmail.com>
- Simon König <simjoko@gmail.com>
- Carlos Knippschild <carlos.chuim@gmail.com>

Special thanks:

- Kristján Valur Jónsson <sweskman@gmail.com>
- Andrew Francis <af.stackless@gmail.com>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
