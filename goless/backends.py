
class Backend(object):
    def start(self, func, *args, **kwargs):
        """Starts a tasklet/greenlet."""
        raise NotImplementedError()

    def run(self, func, *args, **kwargs):
        """Runs a tasklet up until it blocks or finishes."""
        raise NotImplementedError()

    def channel(self):
        """Returns a new channel."""
        raise NotImplementedError()

    def yield_(self):
        """Yields control for other tasklets/greenlets to run."""
        raise NotImplementedError()

    def resume(self, tasklet):
        """Runs the given tasklet/greenlet immediately."""
        raise NotImplementedError()


def make_stackless_backend():
    import stackless

    class StacklessBackend(Backend):
        def start(self, func, *args, **kwargs):
            return stackless.tasklet(func)(*args, **kwargs)

        def run(self, func, *args, **kwargs):
            t = self.start(func, *args, **kwargs)
            t.run()
            return t

        def channel(self):
            return stackless.channel()

        def yield_(self):
            return stackless.schedule()

        def resume(self, tasklet):
            tasklet.run()

    return StacklessBackend()


stackless_backend = make_stackless_backend()
