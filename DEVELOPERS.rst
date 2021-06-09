Hello and welcome!  Thanks for taking the time to work on **goless**.
This guide will help you get set up.

Running the Tests
=================

goless uses `tox`_ for virtual environment setup and test running.
Install tox so that it's accessible on ``$PATH`` somehow.
Then ``cd`` into the goless root and type::

  $ tox

That will install virtual environments and run tests
for all of the "standard" Python interpreters that goless supports
(Stackless interpreters are handled separately. See `Running with Stackless`_).
Some of the environments may need additional build requirements,
such as ``33gevent`` and ``34gevent``,
which need to build ``gevent`` with ``cython``,
but if you get no catastrophic errors you should be good.

For a quick spot check of the tests you can test against a specific version
like this::

  $ tox -e 27gevent

You can look at the ``tox.ini`` to see all available configurations.
It also tells you what the install requirements are,
and should be a help if you want to set up some sort of custom environment.

Finally, please note that the `Travis CI project`_ runs
all the supported configurations, so if you can't test all environments locally,
you'll find out if you broke something once Travis runs.

Running with Stackless
======================

Testing goless with `Stackless Python`_ is a pain
and generally left to dedicated developers (and the CI server).
It should only be needed when you are working on backends,
which should be pretty rare.

In the ``tox.ini`` file, there are a few Stackless Python configurations
that are not normally run locally.
They are run by Travis, but not by default
when you run ``tox`` from the command line.
If you have Stackless Python installed,
you can edit the ``tox.ini`` file to point to your Stackless interpreter.

Otherwise, feel free to ask for help if you get stuck.

All Features Must Have Tests
============================

All features and pretty much all bug fixes must have tests.
There are no exceptions.
Your Pull Request will be denied if new code is not thoroughly tested.

Code Style
==========

Please follow `PEP8`_ for all contributed code.  Specifically, please keep
the window width to 80 chars and follow the PEP8 formatting style.

.. _`tox`: http://codespeak.net/tox/
.. _`Travis CI project`: https://travis-ci.org/rgalanakis/goless
.. _Stackless Python: http://www.stackless.com/
.. _`PEP8`: http://www.python.org/dev/peps/pep-0008/
