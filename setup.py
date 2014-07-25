from setuptools import setup

from goless import version, __author__, __email__, __url__, __license__

requires = ['gevent>=1.0']

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
    install_requires=requires
    packages=['goless'],
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
