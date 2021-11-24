#!/usr/bin/env python

import os
import platform
from packaging.version import parse

from texasbbq import (main,
                      execute,
                      git_ls_remote_tags,
                      git_latest_tag,
                      CondaSource,
                      GitTarget,
                      CondaTarget,
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
                "matplotlib datashader holoviews tensorflow scikit-image"]

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
            "python ipython numpy scipy pip h5py "
            "pytest pytest-benchmark",
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

    @property
    def clone_url(self):
        return "https://github.com/scikit-hep/awkward-1.0.git"

    @property
    def git_ref(self):
        return(git_ls_remote_tags(self.clone_url)[-1])

    def clone(self):
        # Awkward has special needs when cloning, --recursive.
        execute(f"git clone -b {self.git_ref} {self.clone_url} "
                f"--recursive {self.name}")

    @property
    def conda_dependencies(self):
        # Awkward needs more recent compilers, support Linux and MacOSX
        operating_system = platform.uname()[0]
        if operating_system == "Linux":
            compilers = "-c conda-forge gcc_linux-64=9.3 gxx_linux-64=9.3 sysroot_linux-64=2.17"
        elif operating_system == "Darwin":
            compilers = "-c conda-forge clang_osx-64=11.0 clangxx_osx-64=11.0"
        else:
            msg = f"Operating system '{operating_system}' is not supported"
            raise NotImplementedError(msg)
        # Minimal dependencies only, 'localbuild.py'  will call on 'pip' to
        # install the rest.
        return ["python numpy make cmake", compilers]

    @property
    def install_command(self):
        # Switch -j1 is for 'make' parallellistm and --release for cmake mode.
        return "python localbuild.py -j1 --release"

    @property
    def test_command(self):
        # Switch -rfEsxX enables more verbose pytest summary.
        return "pytest -rfEsxX -v tests"

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
        return ["python numpy pandas moto cython setuptools pytest",
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
        return ["python bokeh<2.0 codecov colorcet dask[complete] "
                "datashape fastparquet flake8 nbsmoke numpy pandas pandas "
                "param pillow pyct[cmd] pytest pytest-benchmark pytest-cov "
                "scikit-image scipy toolz xarray==0.16.2 netcdf4"]

    @property
    def install_command(self):
        return "pip install -e ."

    @property
    def test_command(self):
        return "pytest datashader"


class PandasTests(CondaTarget):

    @property
    def name(self):
        return "pandas"

    @property
    def conda_package(self):
        return self.name

    @property
    def conda_dependencies(self):
        return ["python hypothesis pytest"]

    def test(self):
        # Testing pandas has special requirements.
        # See: https://github.com/pandas-dev/pandas/issues/37939

        # Obtain all the paths of the relevant test modules. This uses the
        # subprocess module to execute `conda run`, which then runs a single
        # Python command in the correct environment to import the test module
        # and print it's __file__ attribute.

        paths = []
        for module_subpath in (
            "util",
            "groupby.aggregate",
            "groupby.transform",
            "window",
            ):
            path = execute('conda run -n pandas python -c '
                           '"from pandas.tests.{} import test_numba ; '
                           'print(test_numba.__file__)"'.format(
                               module_subpath), capture=True)
            paths.append(path.decode("utf-8").strip())

        # Run pytest on all the testing modules. This again uses subprocess to
        # execute conda run to run pytest in the correct environment on the
        # correct paths of the test module.
        execute('conda run --no-capture-output -n pandas pytest '
                '{}'.format(" ".join(paths)))


class TardisTests(GitTarget):
    
    @property
    def name(self):
        return "tardis"
    
    @property
    def clone_url(self):
        return "https://github.com/tardis-sn/tardis.git"
    
    @property
    def git_ref(self):
        # This pipeline runs git 2.1.4 and does not support `git describe --tags --abbrev=0` nor 
        # `git tag --sort=committerdate`, etc. Using the GitHub API to get the latest tag.
        import json
        from urllib.request import urlopen

        url = "https://api.github.com/repos/tardis-sn/tardis/releases/latest"
        response = urlopen(url)

        return json.load(response)['tag_name']

    @property
    def conda_dependencies(self):
        return ["-c conda-forge tardis-sn"]  # Install dependencies via YAML file

    @property
    def install_command(self):
        return "conda env update --file tardis_env3.yml && pip install -e ."

    @property
    def test_command(self):
        return "pytest tardis --tardis-refdata=/home/circleci/repo/tardis/tardis-refdata"

    def test(self):
        """ Custom test function for TARDIS. """
        os.chdir(self.name)

        # Download reference data
        ref_data_files = ["atom_data/kurucz_cd23_chianti_H_He.h5", "atom_data/chianti_He.h5",
                          "unit_test_data.h5", "packet_unittest.h5", "montecarlo_1e5_compare_data.h5"]

        execute("mkdir -p tardis-refdata/atom_data")
        for fname in ref_data_files:
            execute(f"wget 'https://dev.azure.com/tardis-sn/TARDIS/_apis/git/repositories/tardis-refdata/items?path={fname}&resolveLfs=true' -O tardis-refdata/{fname}")

        execute("conda run --no-capture-output -n {} {}".format(self.name, self.test_command))
        os.chdir('../')


if __name__ == "__main__":
    main(NumbaSource())
