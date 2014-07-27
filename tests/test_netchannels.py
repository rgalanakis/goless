import subprocess
import sys
import unittest

import goless
import goless.netchannels as nc


SUCCESS = 234

class NetChannelTests(unittest.TestCase):

    def test_inproc(self):
        a = nc.Address()
        c = nc.sender(a)
        s = nc.receiver(a)
        goless.go(c.send, 1)
        got = s.recv()
        self.assertEqual(got, 1)

    def test_out_of_proc(self):
        args = [sys.executable, __file__]
        for port in [4321, 4322, 4323]:
            sendargs = args + [str(port), '--client']
            recvargs = args + [str(port), '--server']
            sendproc = subprocess.Popen(sendargs)
            recvproc = subprocess.Popen(recvargs)
            self.assertEqual(sendproc.wait(), SUCCESS)
            self.assertEqual(recvproc.wait(), SUCCESS)


def main():
    port = int(sys.argv[1])
    addr = nc.Address(port=port)
    if sys.argv[2] == '--client':
        nc.sender(addr).send(port)
    else:
        assert sys.argv[2] == '--server'
        got = nc.receiver(addr).recv()
        if got != port:
            sys.exit('Received %r instead of %r' % (got, port))
    sys.exit(SUCCESS)


if __name__ == '__main__':
    main()
