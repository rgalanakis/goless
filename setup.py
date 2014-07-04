from setuptools import setup

from goless import version, __author__, __email__, __url__, __license__

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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    test_suite='tests',
)
