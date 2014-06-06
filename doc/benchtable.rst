.. table:: Current goless Benchmarks

    ======== ========= ============== =======
    Platform Backend   Benchmark      Time
    ======== ========= ============== =======
    PyPy     stackless chan_async     0.06000
    CPython  stackless chan_async     0.15000
    PyPy     gevent    chan_async     0.30800
    PyPy     stackless chan_buff      0.06400
    CPython  stackless chan_buff      0.14000
    PyPy     gevent    chan_buff      0.30000
    PyPy     stackless chan_sync      0.06000
    CPython  stackless chan_sync      0.14000
    PyPy     gevent    chan_sync      0.31600
    PyPy     stackless select         0.07600
    CPython  stackless select         0.31000
    PyPy     gevent    select         0.38800
    PyPy     stackless select_default 0.00800
    PyPy     gevent    select_default 0.01200
    CPython  stackless select_default 0.14000
    ======== ========= ============== =======
