goless
======

The ``goless`` library provides **golang**-like
semantics built on top of Stackless Python.
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
        _, val = goless.select([goless.rcase(c1), goless.rcase(c2)])
        print(val)

It is surely a testament to Go's style that it isn't much less Python code than Go code,
but I quite like this. Don't you?

Golang: http://www.golang.org
Stackless Python: http://www.stackless.com

Credits
=======

``goless`` is maintained primarily by Rob Galanakis (<rob.galanakis@gmail.com>),
and was created during the PyCon 2014 sprints.
Even a small library like ``goless`` is the product of lots of collaboration.

- Simon König <simjoko@gmail.com>
- Carlos Knippschild <carlos.chuim@gmail.com>
- Kristján Valur Jónsson <sweskman@gmail.com>
- Andrew Francis <af.stackless@gmail.com>
