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
PY3 = os.path.expanduser('~/dev/venvs/go33/bin/python')
EXE_BACKEND_MATRIX = [
    [PYPY, 'stackless'],
    [PYPY, 'gevent'],
    [SLP, 'stackless'],
    [SLP, 'gevent'],
    [PY3, 'gevent']
]
RST = os.path.join('doc', 'benchtable.rst')
COLUMN_WIDTHS = 9, 9, 16, 7

BenchmarkResult = collections.namedtuple(
    'BenchResult', ['platform', 'backend', 'benchmark', 'time'])


def stdout_to_results(s):
    """Turns the multi-line output of a benchmark process into
    a sequence of BenchmarkResult instances."""
    results = s.strip().split('\n')
    return [BenchmarkResult(*r.split()) for r in results]


def get_benchproc_results(clargs, **kwargs):
    p = subprocess.Popen(
        clargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        sys.stderr.write('Failed to benchmark: %s\n' % ' '.join(clargs))
        sys.stderr.write(stderr)
        return []
    results = stdout_to_results(stdout)
    for br in results:
        print(justify_benchresult(br))
    return results


def benchmark_process_and_backend(exe, backend):
    """Returns BenchmarkResults for a given executable and backend."""
    env = dict(os.environ)
    env['GOLESS_BACKEND'] = backend
    args = [exe, '-m', 'benchmark']
    return get_benchproc_results(args, env=env)


def benchmark_go():
    """Writes the go benchmarks, if go is installed."""
    subprocess.check_call(['go', 'version'], stdout=subprocess.PIPE)
    return get_benchproc_results(['go', 'run', 'benchmark.go'])


def collect_results():
    """Runs all platforms/backends/benchmarks and returns as list of
    BenchmarkResults, sorted by benchmark and time taken.
    """
    results = []
    for exe, backendname in EXE_BACKEND_MATRIX:
        results.extend(benchmark_process_and_backend(exe, backendname))
    results.extend(benchmark_go())

    results.sort(
        key=lambda br: (br.benchmark, float(br.time), br.platform, br.backend))
    return results


def insert_seperator_results(results):
    """Given a sequence of BenchmarkResults,
    return a new sequence where a "seperator" BenchmarkResult has been placed
    between differing benchmarks to provide a visual difference."""
    sepbench = BenchmarkResult(*[' ' * w for w in COLUMN_WIDTHS])
    last_bm = None
    for r in results:
        if last_bm is None:
            last_bm = r.benchmark
        elif last_bm != r.benchmark:
            yield sepbench
            last_bm = r.benchmark
        yield r


def justify_benchresult(br):
    middle = '|'.join(br[i].ljust(COLUMN_WIDTHS[i]) for i in range(len(br)))
    return '|%s|' % middle


def make_sepline(char='-'):
    seperator_line = '    +{}+{}+{}+{}+'.format(
        *[char * w for w in COLUMN_WIDTHS])
    return seperator_line


def main():
    print('Running benchmarks.')

    results = insert_seperator_results(collect_results())

    with open(RST, 'w') as f:
        def w(s):
            f.write(s)
            f.write('\n')
            f.flush()

        w('.. table:: Current goless Benchmarks')
        w('')
        w(make_sepline())
        w('    |Platform |Backend  |Benchmark     |Time   |')
        w(make_sepline('='))
        for br in results:
            f.write('    ')
            f.write(justify_benchresult(br))
            f.write('\n')
            f.write(make_sepline())
            f.write('\n')
    print('Benchmarks finished. Report written to %s' % RST)


if __name__ == '__main__':
    main()
