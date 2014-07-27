import cPickle

import zmq.green as zmq


PROTOCOL_TCP = 'tcp'

class Address(object):
    def __init__(self, host='localhost', port=8542, protocol=PROTOCOL_TCP):
        if host in ('localhost', '*'):
            host = '127.0.0.1'
        self.host = host
        self.port = port
        self.protocol = protocol

    def connstr(self):
        return '{}://{}:{}'.format(self.protocol, self.host, self.port)


class sender(object):
    def __init__(self, address):
        self.sock = zmq.Context().socket(zmq.REQ)
        self.sock.connect(address.connstr())

    def send(self, value):
        self.sock.send(cPickle.dumps(value))
        ack = self.sock.recv()
        assert ack == 'ack'


class receiver(object):
    def __init__(self, address):
        self.sock = zmq.Context().socket(zmq.REP)
        self.sock.bind(address.connstr())

    def recv(self):
        value = self.sock.recv()
        self.sock.send('ack')
        return cPickle.loads(value)
