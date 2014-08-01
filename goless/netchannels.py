import cPickle
import errno
import os
import sys

import zmq.green as zmq

from . import compat

PROTOCOL_TCP = 'tcp'

DEBUG = True

PREFIX = ''

_out = sys.__stdout__
def debug(msg, *args):
    if DEBUG:
        _out.write('%s%s: %s\n' % (PREFIX, os.getpid(), str(msg) % args))
        _out.flush()


class Address(object):
    def __init__(self, host='localhost', port=8542, protocol=PROTOCOL_TCP):
        if host in ('localhost', '*'):
            host = '127.0.0.1'
        self.host = host
        self.port = port
        self.protocol = protocol

    def connstr(self):
        return '{0}://{1}:{2}'.format(self.protocol, self.host, self.port)

    def __repr__(self):
        return self.connstr()
    __str__ = __repr__


class _NetChan(object):
    def __init__(self, sock, name):
        self.sock = sock
        self.name = name
        self._closed = False

    def debug(self, msg, *args):
        debug('%s: %s' % (self.name, msg % args))

    def close(self):
        if self._closed:
            return
        self.debug('closing')
        self.sock.close()
        self._closed = True

    def __del__(self):
        self.close()


class sender(_NetChan):
    def __init__(self, address, name='sender'):
        sock = zmq.Context().socket(zmq.REQ)
        sock.connect(address.connstr())
        _NetChan.__init__(self, sock, name)

    def send(self, value):
        self.debug('sending %s', value)
        self.sock.send(cPickle.dumps(value))
        self.debug('receving')
        ack = self.sock.recv()
        self.debug('received ack')
        assert ack == 'ack'


class sender1(sender): pass
class sender2(sender): pass


class receiver(_NetChan):
    def __init__(self, address, name='recver'):
        sock = zmq.Context().socket(zmq.REP)
        try:
            sock.bind(address.connstr())
        except zmq.ZMQError as e:
            if e.errno != errno.EADDRINUSE:
                raise
            raise zmq.ZMQError(e.errno, 'Address %s already in use.' % address)
        _NetChan.__init__(self, sock, name)

    def recv(self, block=True):
        flags = 0
        if not block:
            flags = zmq.NOBLOCK
        self.debug('receiving')
        value = self.sock.recv(flags)
        self.debug('received')
        self.sock.send('ack')
        self.debug('sent ack')
        return cPickle.loads(value)

    def __iter__(self):
        return self

    def _next(self):
        try:
            self.debug('next')
            value = self.recv(False)
        except zmq.Again:
            raise StopIteration
        return value

    if compat.PY3:
        def __next__(self):
            return self._next()
    else:
        def next(self):
            return self._next()

    def drain(self, count):
        assert count >= 1
        results = []
        while len(results) < count:
            results.append(self.recv())
        return results
