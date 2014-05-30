from setuptools import setup

setup(
    name='goless',
    version='0.0.1',
    author='Rob Galanakis',
    author_email='rob.galanakis@gmail.com',
    description="goless puts Go's channels and select into Python.",
    long_description="""goless provides Go-like channels and a select function
    in Python, written on top of Stackless Python.
    You can **send** to and **recv** from buffered or unbuffered **channels**,
    and use a Go-like **select** function.
    It also has goroutines for good measure.
    """,
    license='Apache',
    keywords='tasklet stackless go concurrent threading async',
    url='https://github.com/rgalanakis/goless',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
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
