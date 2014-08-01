import errno
import os
import subprocess
import sys
import unittest
import zmq

import goless
import goless.netchannels as nc
from tests import BaseTests


SUCCESS = 234
CLIENT_COUNT = 6
INPUT_PORTS = [4321, 4322, 4323]
OUTPUT_PORT = 4320
SIMPLE_PORT = 4319
DRAIN_PORT = 4318
DEL_PORT = 4317


class NetChannelTests(BaseTests):

    def setUp(self):
        BaseTests.setUp(self)
        nc.PREFIX = self._testMethodName

    def popen(self, *args):
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(
            sys.path + [os.environ.get('PYTHONPATH', '')])
        clargs = [sys.executable, __file__] + [str(a) for a in args]
        proc = subprocess.Popen(clargs, env=env)
        nc.debug('Started proc %s: %s', proc.pid, args)

        def safeterm():
            try:
                proc.terminate()
            except OSError as ex:
                assert ex.errno == errno.ESRCH
        self.addCleanup(safeterm)
        return proc

    def test_simple(self):
        a = nc.Address(port=SIMPLE_PORT)
        s = nc.sender1(a)
        r = nc.receiver(a)
        got = []
        goless.go(lambda: got.append(r.recv()))
        s.send(1)
        # goless.go(s.send, 1)
        # s.send(1)
        # got = r.recv()
        self.assertEqual(got, [1])

    def test_drain(self):
        cnt = 2
        a = nc.Address(port=DRAIN_PORT)
        r = nc.receiver(a)
        senders = [nc.sender2(a) for _ in range(cnt)]
        for i, s in enumerate(senders):
            goless.go(s.send, i * 2)
        got = r.drain(cnt)
        self.assertEqual(sorted(got), [i * 2 for i in range(cnt)])

    def test_complex_outofproc(self):
        output_chan = nc.receiver(
            nc.Address(port=OUTPUT_PORT), 'output-recver')
        procs = []
        ideal_datas = []
        for input_port in INPUT_PORTS:
            procs.append(self.popen(input_port, '--server'))
            for i in range(CLIENT_COUNT):
                procs.append(self.popen(input_port, '--client', i))
                ideal_datas.append(_process(i))
        results = output_chan.drain(len(INPUT_PORTS * CLIENT_COUNT))
        for proc in procs:
            self.assertEqual(proc.wait(), SUCCESS)
        self.assertEqual(sorted(results), sorted(ideal_datas))

    def test_close_socket_when_del(self):
        sock = zmq.Context().socket(zmq.REQ)
        a = nc.Address(port=DEL_PORT)
        r = nc.receiver(a)
        with self.assertRaises(zmq.ZMQError):
            sock.bind(a.connstr())
        del r
        sock.bind(a.connstr())
        sock.close()


def _process(v):
    return v ** 2


def _server(work_addr, results_addr):
    workchan = nc.receiver(work_addr, 'input-recver')
    outputchan = nc.sender(results_addr, 'output-sender')
    for _ in range(CLIENT_COUNT):
        data = workchan.recv()
        result = _process(data)
        outputchan.send(result)
    workchan.close()
    outputchan.close()
    nc.debug('output-sender exiting.')
    sys.exit(SUCCESS)


def _client(work_addr, value):
    workchan = nc.sender(work_addr, 'input-sender')
    workchan.send(value)
    workchan.close()
    nc.debug('input-sender exiting.')
    sys.exit(SUCCESS)


def main(argv=sys.argv):
    work_addr = nc.Address(port=int(argv[1]))
    if argv[2] == '--client':
        value = int(argv[3])
        _client(work_addr, value)
    else:
        assert argv[2] == '--server'
        results_addr = nc.Address(port=OUTPUT_PORT)
        _server(work_addr, results_addr)
    assert False, 'Should not reach here!'


if __name__ == '__main__':
    main()
