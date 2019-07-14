#!/usr/bin/env python

import os

from texasbbq import (main,
                      execute,
                      conda_install,
                      git_ls_remote_tags,
                      IntegrationTestCondaSource,
                      IntegrationTestProject,
                      )


class NumbaSource(IntegrationTestCondaSource):

    module = __name__

    @property
    def name(self):
        return "numba"

    @property
    def conda_package(self):
        return "-c numba/label/dev numba"


class UmapTests(IntegrationTestProject):
    @property
    def name(self):
        return "umap"

    @property
    def clone_url(self):
        return "https://github.com/lmcinnes/umap"

    @property
    def target_tag(self):
        return([t for t in git_ls_remote_tags(self.clone_url) if not
                t.startswith("v")][-1])

    @property
    def conda_dependencies(self):
        return ["numpy scikit-learn scipy nose"]

    def install(self):
        execute("pip install -e .")

    def run_tests(self):
        execute("nosetests -s umap")


class HpatTests(IntegrationTestProject):
    @property
    def name(self):
        return "hpat"

    @property
    def conda_dependencies(self):
        return ["pyspark openjdk scipy", "-c ehsantn h5py"]

    def install(self):
        conda_install(
            self.name, "-c ehsantn -c anaconda -c conda-forge hpat"
        )

    def run_tests(self):
        execute("python -m hpat.tests.gen_test_data")
        execute("python -m hpat.runtests")


class LibrosaTests(IntegrationTestProject):
    @property
    def name(self):
        return "librosa"

    @property
    def clone_url(self):
        return "https://github.com/librosa/librosa.git"

    @property
    def target_tag(self):
        return([t for t in git_ls_remote_tags(self.clone_url) if not
                t.startswith("v")][-1])

    @property
    def conda_dependencies(self):
        return [
            "pip numpy scipy coverage scikit-learn matplotlib pytest",
            "-c conda-forge ffmpeg pysoundfile",
        ]

    def install(self):
        execute("pip install --pre -e .[tests]")

    def run_tests(self):
        execute("pytest")


class CliffordTests(IntegrationTestProject):

    @property
    def name(self):
        return "clifford"

    @property
    def clone_url(self):
        return "https://github.com/pygae/clifford.git"

    @property
    def target_tag(self):
        return(git_ls_remote_tags(self.clone_url)[-1])

    @property
    def conda_dependencies(self):
        return [
            "future numpy scipy numba pip nose h5py",
        ]

    def install(self):
        execute("python setup.py install")

    def run_tests(self):
        execute("nosetests")


class AwkwardTests(IntegrationTestProject):
    @property
    def name(self):
        return "awkward"

    @property
    def clone_url(self):
        return "https://github.com/scikit-hep/awkward-array"

    @property
    def target_tag(self):
        return([t for t in git_ls_remote_tags(self.clone_url)
                if "rc" not in t][-1])

    @property
    def conda_dependencies(self):
        return ["numpy pytest"]

    def install(self):
        execute("python setup.py install")
        os.chdir("awkward-numba")
        execute("python setup.py install")
        os.chdir("..")

    def run_tests(self):
        execute("pytest -v tests/test_numba.py")   # only the test that uses Numba


class SparseTests(IntegrationTestProject):

    @property
    def name(self):
        return "sparse"

    @property
    def clone_url(self):
        return "https://github.com/pydata/sparse.git"

    @property
    def target_tag(self):
        return git_ls_remote_tags(self.clone_url)[-1]

    @property
    def conda_dependencies(self):
        return ["pip numpy scipy"]

    def install(self):
        execute("pip install -e .[all]")

    def run_tests(self):
        execute("pytest")


class FastparquetTests(IntegrationTestProject):

    @property
    def name(self):
        return "fastparquet"

    @property
    def clone_url(self):
        return "https://github.com/dask/fastparquet.git"

    @property
    def target_tag(self):
        return([t for t in git_ls_remote_tags(self.clone_url)
                if not t == "1.1"][-1])

    @property
    def conda_dependencies(self):
        return ["numpy pandas pytest<5.0.0"
                "brotli thrift python-snappy lz4 s3fs moto cython setuptools ",
                "-c conda-forge bson zstandard python-lzo",
                ]

    def install(self):
        execute("python setup.py install")

    def run_tests(self):
        os.environ["AWS_ACCESS_KEY_ID"] = "1111"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "2222"
        execute("python setup.py test")
        os.environ.pop("AWS_ACCESS_KEY_ID")
        os.environ.pop("AWS_SECRET_ACCESS_KEY")


class PygbmTests(IntegrationTestProject):

    @property
    def name(self):
        return "pygbm"

    @property
    def clone_url(self):
        return "https://github.com/ogrisel/pygbm.git"

    @property
    def target_tag(self):
        return(git_ls_remote_tags(self.clone_url)[-1])

    @property
    def conda_dependencies(self):
        return ["scipy scikit-learn pytest joblib lightgbm"]

    def install(self):
        execute("pip install --editable .")

    def run_tests(self):
        execute("pytest")


if __name__ == "__main__":
    main(NumbaSource())
