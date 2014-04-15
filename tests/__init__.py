import stacklesslib.util as _sutil


def run_tasklet(func, *args, **kwargs):
    return _sutil.tasklet_run(func, args, kwargs)


def start_tasklet(func, *args, **kwargs):
    return _sutil.tasklet_new(func, *args, **kwargs)
