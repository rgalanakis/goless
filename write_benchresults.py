"""
Updates the doc/benchtable.rst file.
Must be run from project folder.
Set up to work on Rob's machine.
Configre PYPY and SLP constants for your computer to run locally.

Can generalize it if needed,
or if we figure out a better way to handle benchmarks.
"""

from __future__ import print_function

import collections
import subprocess
import sys

import os


PYPY = os.path.expanduser('~/venvs/gopypy/bin/python')
SLP = os.path.expanduser('~/dev/venvs/go27slp/bin/python')
RST = os.path.join('doc', 'benchtable.rst')
COLUMN_WIDTHS = 8, 9, 14, 7

BenchmarkResult = collections.namedtuple(
    'BenchResult', ['platform', 'backend', 'benchmark', 'time'])


def stdout_to_results(s):
    """Turns the multi-line output of a benchmark process into
    a sequence of BenchmarkResult instances."""
    results = s.strip().split('\n')
    return [BenchmarkResult(*r.split()) for r in results]


def benchmark_process_and_backend(exe, backend):
    """Returns BenchmarkResults for a given executable and backend."""
    env = dict(os.environ)
    env['GOLESS_BACKEND'] = backend
    args = [exe, '-m', 'benchmark']
    p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, args, stderr)
    return stdout_to_results(stdout)


def collect_results():
    """Runs all platforms/backends/benchmarks and returns as list of
    BenchmarkResults, sorted by benchmark and time taken.
    """
    # call('stackless')
    results = []
    for exe in PYPY, SLP:
        for be in 'gevent', 'stackless':
            try:
                results.extend(benchmark_process_and_backend(exe, be))
            except subprocess.CalledProcessError as ex:
                sys.stderr.write(
                    'Failed to benchmark: {} {}\n'.format(exe, be))
                sys.stderr.write(ex.output)
    results.sort(
        key=lambda br: (br.benchmark, br.time, br.platform, br.backend))
    return results


def insert_seperator_results(results):
    """Given a sequence of BenchmarkResults,
    return a new sequence where a "seperator" BenchmarkResult has been placed
    between differing benchmarks to provide a visual difference."""
    sepbench = BenchmarkResult(*['~' * w for w in COLUMN_WIDTHS])
    last_bm = None
    for r in results:
        if last_bm is None:
            last_bm = r.benchmark
        elif last_bm != r.benchmark:
            yield sepbench
            last_bm = r.benchmark
        yield r


def main():
    results = insert_seperator_results(collect_results())
    seperator_line = '    {} {} {} {}'.format(
        *['=' * w for w in COLUMN_WIDTHS])
    with open(RST, 'w') as f:
        w = lambda s: print(s, file=f)
        w('.. table:: Current goless Benchmarks')
        w('')
        w(seperator_line)
        w('    Platform Backend   Benchmark      Time')
        w(seperator_line)
        for br in results:
            f.write('    ')
            f.write(' '.join(
                br[i].ljust(COLUMN_WIDTHS[i]) for i in range(len(br))))
            f.write('\n')
        w(seperator_line)


if __name__ == '__main__':
    main()
