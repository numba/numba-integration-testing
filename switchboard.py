#!/usr/bin/env python

import os
from packaging.version import parse

from texasbbq import (main,
                      execute,
                      git_ls_remote_tags,
                      git_latest_tag,
                      CondaSource,
                      GitTarget,
                      )


class NumbaSource(CondaSource):

    module = __name__

    @property
    def name(self):
        return "numba"

    @property
    def conda_package(self):
        return "--update-specs numba/label/dev::numba"


class UmapTests(GitTarget):
    @property
    def name(self):
        return "umap"

    @property
    def clone_url(self):
        return "https://github.com/lmcinnes/umap"

    @property
    def git_ref(self):
        return([t for t in git_ls_remote_tags(self.clone_url) if not
                t.startswith("v")][-1])

    @property
    def conda_dependencies(self):
        return ["numpy pytest nose scikit-learn pynndescent scipy pandas bokeh "
                "matplotlib datashader holoviews"]

    @property
    def install_command(self):
        return "pip install -e ."

    @property
    def test_command(self):
        return "pytest"


class LibrosaTests(GitTarget):
    @property
    def name(self):
        return "librosa"

    @property
    def clone_url(self):
        return "https://github.com/librosa/librosa.git"

    @property
    def git_ref(self):
        return([t for t in git_ls_remote_tags(self.clone_url) if not
                t.startswith("v")][-1])

    @property
    def conda_dependencies(self):
        return [
            "pip numpy scipy coverage scikit-learn matplotlib pytest",
        ]

    @property
    def install_command(self):
        return "conda install -c conda-forge ffmpeg pysoundfile && pip install --pre -e .[tests]"

    @property
    def test_command(self):
        return "pytest"


class CliffordTests(GitTarget):

    @property
    def name(self):
        return "clifford"

    @property
    def clone_url(self):
        return "https://github.com/pygae/clifford.git"

    @property
    def git_ref(self):
        return(git_ls_remote_tags(self.clone_url)[-1])

    @property
    def conda_dependencies(self):
        return [
            "ipython numpy scipy pip h5py pytest pytest-benchmark",
            "-c conda-forge sparse",
        ]

    @property
    def install_command(self):
        return "python setup.py install"

    @property
    def test_command(self):
        return "pytest -v clifford/test"


class AwkwardTests(GitTarget):

    @property
    def name(self):
        return "awkward"

    def clone(self):
        execute("git clone https://github.com/scikit-hep/awkward-1.0.git "
                "--recursive awkward")

    @property
    def conda_dependencies(self):
        return ["python<=3.8 numpy pytest make cmake"]

    @property
    def install_command(self):
        return "true"

    @property
    def test_command(self):
        return "python localbuild.py --pytest tests"

class SparseTests(GitTarget):

    @property
    def name(self):
        return "sparse"

    @property
    def clone_url(self):
        return "https://github.com/pydata/sparse.git"

    @property
    def git_ref(self):
        return git_latest_tag(self.clone_url, vprefix=False)

    @property
    def conda_dependencies(self):
        return ["pip numpy scipy"]

    @property
    def install_command(self):
        return "pip install -e .[all]"

    @property
    def test_command(self):
        return "pytest --pyargs sparse"


class FastparquetTests(GitTarget):

    @property
    def name(self):
        return "fastparquet"

    @property
    def clone_url(self):
        return "https://github.com/dask/fastparquet.git"

    @property
    def git_ref(self):
        return([t for t in git_ls_remote_tags(self.clone_url)
                if not t == "1.1"][-1])

    @property
    def conda_dependencies(self):
        return ["python numpy pandas==1.0.5 moto cython setuptools pytest",
                # compression algos available via defaults/main
                "brotli thrift python-snappy lz4",
                # compression algos available via conda-forge
                "-c conda-forge bson python-lzo s3fs",
                # zstandard and zstd was a mess on anaconda.org at the time of
                # writing, so enable setup.py to pull in versions from PyPi
                ]

    @property
    def install_command(self):
        return "python setup.py install"

    @property
    def test_command(self):
        return "python setup.py test"

    # Tetsts need to futz about with the environment
    def test(self):
        os.environ["AWS_ACCESS_KEY_ID"] = "1111"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "2222"
        super().test()
        os.environ.pop("AWS_ACCESS_KEY_ID")
        os.environ.pop("AWS_SECRET_ACCESS_KEY")


class PygbmTests(GitTarget):

    @property
    def name(self):
        return "pygbm"

    @property
    def clone_url(self):
        return "https://github.com/ogrisel/pygbm.git"

    @property
    def git_ref(self):
        return(git_ls_remote_tags(self.clone_url)[-1])

    @property
    def conda_dependencies(self):
        return ["scipy scikit-learn pytest joblib lightgbm"]

    @property
    def install_command(self):
        return "pip install --editable ."

    @property
    def test_command(self):
        return "pytest"


class DatashaderTests(GitTarget):

    @property
    def name(self):
        return "datashader"

    @property
    def clone_url(self):
        return "https://github.com/holoviz/datashader.git"

    @property
    def git_ref(self):
        return "v" + str(sorted([parse(t)
                   for t in git_ls_remote_tags(self.clone_url)])[-1])

    @property
    def conda_dependencies(self):
        return ["python<3.8 bokeh<2.0 codecov colorcet dask[complete] "
                "datashape fastparquet flake8 nbsmoke numpy pandas pandas "
                "param pillow pyct[cmd] pytest pytest-benchmark pytest-cov "
                "scikit-image scipy toolz xarray"]

    @property
    def install_command(self):
        return "pip install -e ."

    @property
    def test_command(self):
        return "pytest datashader"


if __name__ == "__main__":
    main(NumbaSource())
