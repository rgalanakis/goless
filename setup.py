from setuptools import setup

setup(
    name='goless',
    version='0.0.4',
    author='Rob Galanakis',
    author_email='rob.galanakis@gmail.com',
    description="Provides a Go-like concurrent programming style in Python.",
    long_description="""goless provides Go-like channels and a select function
    in Python, written on top of gevent, PyPy, or Stackless Python.
    Using goless, you can write Go-style concurrent programs in Python.
    """,
    license='Apache',
    keywords='tasklet stackless go concurrent '
             'threading async gevent go golang',
    url='https://github.com/rgalanakis/goless',
    packages=['goless'],
    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 3',
    ],
    test_suite='tests',
)
