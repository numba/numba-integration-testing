Numba Integration Test
======================

As part of the continuous quality assurance of the `Numba project
<https://numba.pydata.org/>`_ we test the compatability of Numba with the
latests releases of specific libraries that make heavy use of Numba. The target
Numba version to test with, will be the latest version of the git
``master`` branch where the test suite passed.

Usage
-----

The main entry point is a single script ``switchboard.py`` which is used to
drive the integration test. This script will run on at least Python 2.7 and
3.7 and has zero third-party dependencies.

It has multiple *stages*, which are things to perform and multiple *targets*,
which are projects to be tested.

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
