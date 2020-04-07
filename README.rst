=========================
Numba Integration Testing
=========================

As part of the continuous quality assurance of the `Numba project
<https://numba.pydata.org/>`_ we test the compatibility of Numba with the
latests releases of specific dependents, i.e. libraries that make heavy use of
Numba. The target Numba version to test with, will be the latest version of the
git ``master`` branch where the test suite passed. Configurations for both
`CircleCI <https://circleci.com/>`_  and `Travis CI <https://travis-ci.org/>`_
are provided but currently (April 2019) only the CircleCI configuration is
active.

:CircleCI: |circleci|

.. |circleci| image:: https://circleci.com/gh/numba/numba-integration-testing/tree/master.svg?style=svg
    :target: https://circleci.com/gh/numba/numba-integration-testing/tree/master

This setup uses `TexasBBQ <https://github.com/numba/texasbbq>`_ under the hood.

Tested Projects
===============

* `umap <https://umap-learn.readthedocs.io/en/latest/>`_
* `librosa <https://librosa.github.io/librosa/>`_
* `clifford <https://clifford.readthedocs.io/en/latest/>`_
* `awkward-array <https://github.com/scikit-hep/awkward-array>`_
* `pydata/sparse <https://github.com/pydata/sparse.git>`_
* `fastparquet <https://github.com/dask/fastparquet>`_
* `pygbm <https://github.com/ogrisel/pygbm>`_

Temporarily Disabled
====================

* `hpat <https://github.com/IntelLabs/hpat>`_


Adding a new Target
===================

In order to add a new target, you need to:

* Implement the logic for the target, by subclassing ``texasbbq.CondaTarget``
  or ``texasbbq.GitTarget`` in the file ``switchboard.py`` and overloading
  necessary methods.
* Add an appropriate stanza in the CI configuration file
  ``.circleci/config.yml``.
* Updating the ``README.rst`` to reflect the current list of projects being
  tested.
* Submit a pull-request on Github.

Testing a Branch or Pull-Request
================================

Normally, Numba is installed as a conda packge from https://anaconda.org using
a ``CondaSource`` configuration. Sometimes it can be useful to run the
integration-testing from a branch or a pull-request however. The following
configuration demonstrates how to obtain the branch ``refactor_it``
from the Github fork at ``github.com/esc/numba``:

.. code:: python

    class NumbaSource(GitSource):

        module = __name__

        @property
        def name(self):
            return "numba"

        @property
        def clone_url(self):
            return "git://github.com/esc/numba"

        @property
        def git_ref(self):
            return "refactor_it"

        @property
        def conda_dependencies(self):
            return ["-c numba/label/dev llvmlite",
                    "numpy pyyaml colorama scipy jinja2 cffi ipython ",
                    "gcc_linux-64 gxx_linux-64",
                    ]

        @property
        def install_command(self):
            return "python setup.py build_ext -i && "
                   "python setup.py develop --no-deps"

License
=======

Copyright 2019 Anaconda Inc. Licensed under the terms of the BSD two-clause
license. See the file ``LICENSE`` for details.
