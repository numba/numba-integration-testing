=========================
Numba Integration Testing
=========================

As part of the continuous quality assurance of the `Numba project
<https://numba.pydata.org/>`_ we test the compatibility of Numba with the
latests releases of specific dependents, i.e. libraries that make heavy use of
Numba. The target Numba version to test with, will be the latest version of the
git ``master`` branch where the test suite passed. Configurations for both
`CircleCI <https://circleci.com/>`_  and `Travis CI <https://travis-ci.org/>`_
are provided but currently (April 2019) only the CircleCI confguration is
active.

Usage
=====

The main entry point is a single script ``switchboard.py`` which is used to
drive the integration test. This script will run on at least Python 2.7 and 3.7
and has zero third-party dependencies, so it will probably run on a large
variety of different CI systems and platforms. It will download and bootstrap a
self contained miniconda distribution to ensure as clean a build as possible.
You can also run it locally in case you need to debug a build or want to add a
new project to test.

It has multiple *stages*, which are things to perform and multiple *targets*,
which are projects to be tested.

Targets
-------

Targets are projects that should be tested as part of the integration tests.
In an ideal case, the project ships the tests and running the tests is simply a
matter of installing the (potentially pre-compiled) conda package and running
the tests. In case this isn't possible, doing a ``git clone``, building the
package from source and running the tests from the clone is also supported.
The ``switchboard.py`` contains a class ``NumbaIntegrationTestTarget``. Adding
projects involves creating a subclass and filling in the blanks. The
``switchboard.py`` will automatically detect any such subclasses and make them
available.


Stages
------

The stages are as follows:

miniconda
  Download and setup miniconda distribution.

clone
  Git clone any of the targets that require it.

environment
  Setup conda environments for each of the targets.

install
  Install each target.

tests
  Run tests for each target.

The three stages: ``miniconda``, ``clone`` and ``environment`` are more or less
idempotent.  I.e. if miniconda has been downloaded and installed that step will
not be done again.

By default, all stages and all targets will be run. If you want to limit the
stages use the ``-s`` or ``--stages`` switch. If you want to limit the targets
use the ``-t`` or ``--targets`` switch.

Examples::

    # Only download and install miniconda
    $ ./switchboard.py -s miniconda

    # Only run tests for hpat
    $ ./switchboard.py -s hpat

    # Only download miniconda, git clone and setup environment for umap
    $ ./switchboard.py -s miniconda clone environment -t umap

Please see the output of ``./switchboard.py -h`` for more information.

Caveats
=======

* The script is reasonably robust but won't respond well to malformed user
  input. For example, if you try to run only the ``test`` stage without the
  others it is likely to fail.

* If you are running this locally and you already have an anaconda or miniconda
  distribution activated you may run into problems. In such cases it is best to
  run this script from a vanilla (non-customized) shell.

License
=======

Copyright 2019 Anaconda Inc. Licensed under the terms of the BSD two-clause
license. See the file ``LICENSE`` for details.
