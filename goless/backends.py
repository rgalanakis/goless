from __future__ import absolute_import

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

    def propogate_exc(self, errtype, *args):
        """Propogates an exception (created via ``errtype(*args)``)
        so the program hears it and it doesn't die lonely in a tasklet."""
        raise NotImplementedError()


def _make_stackless():
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

        def propogate_exc(self, errtype, *args):
            stackless.getmain().throw(errtype, *args)

    return StacklessBackend()


def _make_gevent():
    import gevent
    import gevent.queue

    class Channel(gevent.queue.Channel):
        def send(self, value):
            self.put(value)

        def receive(self):
            return self.get()

    class GeventBackend(Backend):
        def start(self, func, *args, **kwargs):
            greenlet = gevent.spawn(func, *args, **kwargs)
            return greenlet

        def run(self, func, *args, **kwargs):
            greenlet = gevent.spawn(func, *args, **kwargs)
            gevent.sleep()
            return greenlet

        def channel(self):
            return Channel()

        def yield_(self):
            gevent.sleep()

        def resume(self, tasklet):
            gevent.sleep()

        def propogate_exc(self, errtype, *args):
            raise errtype

    return GeventBackend()

current = _make_stackless()
#current = _make_gevent()