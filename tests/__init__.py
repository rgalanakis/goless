import stacklesslib.util as _sutil


def run_tasklet(func, *args, **kwargs):
    """Runs a tasklet up until it blocks and releases control."""
    return _sutil.tasklet_run(func, args, kwargs)


def start_tasklet(func, *args, **kwargs):
    """Creates and starts a new tasklet."""
    return _sutil.tasklet_new(func, *args, **kwargs)
