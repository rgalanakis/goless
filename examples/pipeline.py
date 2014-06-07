"""
This file demonstrates the pipeline pattern.
A pipeline is used where a series of steps (goroutines) process
data in serial.

The example calculates the md5 checksums
for all files in the current directory.
It is split into a stage that reads the file in the folder,
a stage that calculates the md5 using several goroutines,
and a stage that collects the results.

See http://blog.golang.org/pipelines for more info.
"""
from __future__ import print_function

import hashlib

import os

import goless


def pipeline():
    files = goless.chan()
    hashes = goless.chan()
    results = goless.chan()

    def scanner():
        for d, dn, f in os.walk('.'):
            for fn in f:
                files.send(os.path.join(d,fn))
        files.close()

    def hasher():
        for f in files:
            with open(f, 'rb') as fd:
                md5 = hashlib.md5(fd.read()).hexdigest()
                hashes.send((f, md5))
        hashes.close()

    def collector():
        for f, md5 in hashes:
            results.send((f, md5))
        results.close()

    goless.go(scanner)
    goless.go(hasher)
    goless.go(collector)

    for filename, md5hash in results:
        print('%s: %s' % (filename, md5hash))


if __name__ == '__main__':
    pipeline()
