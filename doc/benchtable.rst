.. table:: Current goless Benchmarks

    ======== ========= ============== =======
    Platform Backend   Benchmark      Time
    ======== ========= ============== =======
    PyPy     stackless chan_async     0.06800
    CPython  stackless chan_async     0.14000
    PyPy     gevent    chan_async     0.35600
    PyPy     stackless chan_buff      0.06400
    CPython  stackless chan_buff      0.14000
    PyPy     gevent    chan_buff      0.36000
    PyPy     stackless chan_sync      0.06000
    CPython  stackless chan_sync      0.14000
    PyPy     gevent    chan_sync      0.75600
    PyPy     stackless select         0.07200
    CPython  stackless select         0.32000
    PyPy     gevent    select         0.44000
    PyPy     gevent    select_default 0.00800
    PyPy     stackless select_default 0.00800
    CPython  stackless select_default 0.14000
    ======== ========= ============== =======
