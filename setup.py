from setuptools import setup
import sys
import warnings

from goless import version, __author__, __email__, __url__, __license__

# If stackless isn't found, then assume gevent needs to be installed.
requires = []
try:
    # noinspection PyUnresolvedReferences
    import stackless
except ImportError:
    # See https://github.com/rgalanakis/goless/issues/21
    # for why we need this (waiting for new gevent version).
    if sys.version_info[0] == 3:
        warnings.warn(
            'You will need to install gevent from GitHub to use goless with '
            'gevent under Python3. Run something like '
            '"pip install git+https://github.com/surfly/gevent.git#gevent-egg"'
        )
    else:
        requires.append('gevent>=1.0')

setup(
    name='goless',
    version=version,
    author=__author__,
    author_email=__email__,
    description="Provides a Go-like concurrent programming style in Python.",
    long_description=open('README.rst').read(),
    license=__license__,
    keywords='tasklet stackless go concurrent '
             'threading async gevent go golang',
    url=__url__,
    packages=['goless'],
    install_requires=requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
