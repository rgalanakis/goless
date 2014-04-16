import stackless as _stackless


def run_tasklet(func, *args, **kwargs):
    """Runs a tasklet up until it blocks and releases control."""
    t = start_tasklet(func, *args, **kwargs)
    t.run()
    return t


def start_tasklet(func, *args, **kwargs):
    """Creates and starts a new tasklet."""
    return _stackless.tasklet(func)(*args, **kwargs)
