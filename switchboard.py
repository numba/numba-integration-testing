#!/usr/bin/env python

import os

from texasbbq import (main,
                      execute,
                      git_clone_ref,
                      git_ls_remote_tags,
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
        return "-c numba/label/dev numba"


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
        return ["numpy scikit-learn scipy nose"]

    @property
    def install_command(self):
        return "pip install -e ."

    @property
    def test_command(self):
        return "nosetests -s umap"


#class HpatTests(GitTarget):
#    @property
#    def name(self):
#        return "hpat"
#
#    @property
#    def conda_dependencies(self):
#        return ["pyspark openjdk scipy", "-c ehsantn h5py"]
#
#    def install(self):
#        conda_install(
#            self.name, "-c ehsantn -c anaconda -c conda-forge hpat"
#        )
#
#    def run_tests(self):
#        execute("python -m hpat.tests.gen_test_data")
#        execute("python -m hpat.runtests")


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
            "-c conda-forge ffmpeg pysoundfile",
        ]

    @property
    def install_command(self):
        return "pip install --pre -e .[tests]"

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
            "future numpy scipy numba pip nose h5py",
        ]

    @property
    def install_command(self):
        return "python setup.py install"

    @property
    def test_command(self):
        return "nosetests"


class AwkwardTests(GitTarget):
    @property
    def name(self):
        return "awkward"

    @property
    def clone_url(self):
        return "https://github.com/scikit-hep/awkward-array"

    @property
    def git_ref(self):
        return([t for t in git_ls_remote_tags(self.clone_url)
                if "rc" not in t][-1])

    @property
    def conda_dependencies(self):
        return ["numpy pytest"]

    # awkward has a unique, multi-command install
    def install(self):
        if not os.path.exists(self.name):
            git_clone_ref(self.clone_url, self.git_ref, self.name)
        os.chdir(self.name)
        execute("conda run -n {} {}".format(self.name,
                                            "python setup.py install"))
        os.chdir("awkward-numba")
        execute("conda run -n {} {}".format(self.name,
                                            "python setup.py install"))
        os.chdir('../../')

    @property
    def test_command(self):
        # only the test that uses Numba
        return "pytest -v tests/test_numba.py"


class SparseTests(GitTarget):

    @property
    def name(self):
        return "sparse"

    @property
    def clone_url(self):
        return "https://github.com/pydata/sparse.git"

    @property
    def git_ref(self):
        return git_ls_remote_tags(self.clone_url)[-1]

    @property
    def conda_dependencies(self):
        return ["pip numpy scipy"]

    @property
    def install_command(self):
        return "pip install -e .[all]"

    @property
    def test_command(self):
        return "pytest"


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
        return ["numpy pandas pytest<5.0.0"
                "brotli thrift python-snappy lz4 s3fs moto cython setuptools ",
                "-c conda-forge bson zstandard python-lzo",
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
        return ["scipy=1.1.0 scikit-learn pytest joblib lightgbm"]

    @property
    def install_command(self):
        return "pip install --editable ."

    @property
    def test_command(self):
        return "pytest"


if __name__ == "__main__":
    main(NumbaSource())
