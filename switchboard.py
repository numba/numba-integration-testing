#!/usr/bin/env python

import argparse
import inspect
import os
import shlex
import subprocess
import sys
import json

MINICONDA_BASE_URL = "https://repo.continuum.io/miniconda/"
MINCONDA_FILE_TEMPLATE = "Miniconda3-latest-{}.sh"
MINCONDA_INSTALLER = "miniconda.sh"
MINCONDA_PATH = "miniconda3"
MINCONDA_FULL_PATH = os.path.join(os.getcwd(), MINCONDA_PATH)
MINCONDA_BIN_PATH = os.path.join(MINCONDA_FULL_PATH, "bin")
MINCONDA_CONDABIN_PATH = os.path.join(MINCONDA_FULL_PATH, "condabin")

LINUX_X86 = "Linux-x86"
LINUX_X86_64 = "Linux-x86_64"
MACOSX_X86_64 = "MacOSX-x86_64"

STAGE_MINICONDA = "miniconda"
STAGE_CLONE = "clone"
STAGE_ENVIRONMENT = "environment"
STAGE_INSTALL = "install"
STAGE_TESTS = "tests"
ALL_STAGES = [
    STAGE_MINICONDA,
    STAGE_CLONE,
    STAGE_ENVIRONMENT,
    STAGE_INSTALL,
    STAGE_TESTS,
]


PREFIX = "::>>"


def echo(value):
    print("{} {}".format(PREFIX, value))


def execute(command, capture=False):
    echo("running: '{}'".format(command))
    if capture:
        return subprocess.check_output(shlex.split(command))
    else:
        subprocess.check_call(shlex.split(command))


UNAME = execute("uname", capture=True).strip().decode("utf-8")


def miniconda_url():
    if UNAME == "Linux":
        filename = MINCONDA_FILE_TEMPLATE.format(LINUX_X86_64)
    elif UNAME == "Darwin":
        filename = MINCONDA_FILE_TEMPLATE.format(MACOSX_X86_64)
    else:
        raise ValueError("Unsupported OS")
    return MINICONDA_BASE_URL + filename


def wget_conda(url, output):
    execute("wget {} -O {}".format(url, output))


def install_miniconda(install_path):
    execute("bash miniconda.sh -b -p {}".format(install_path))


def inject_conda_path():
    os.environ["PATH"] = ":".join(
        [MINCONDA_BIN_PATH, MINCONDA_CONDABIN_PATH]
        + os.environ["PATH"].split(":")
    )


def switch_environment_path(env):
    os.environ["PATH"] = ":".join(
        [os.path.join(conda_environments()[env], "bin")]
        + os.environ["PATH"].split(":")[1:]
    )


def git_clone(url):
    execute("git clone {}".format(url))


def git_clone_tag(url, tag):
    execute("git clone -b {} {} --depth=1".format(tag, url))


def git_tag():
    return execute("git tag", capture=True).split('\n')


def git_ls_remote_tags(url):
    return [os.path.basename(line.split("\t")[1])
            for line in execute("git ls-remote --tags --refs {}".format(url),
            capture=True).decode("utf-8").split("\n") if line]


def git_checkout(tag):
    execute("git checkout {}".format(tag))


def conda_update_conda():
    execute("conda update -y -n base -c defaults conda")


def conda_environments():
    return dict(
        (
            (os.path.basename(i), i)
            for i in json.loads(
                execute("conda env list --json", capture=True)
            )["envs"]
        )
    )


def conda_create_env(name):
    execute("conda create -y -n {}".format(name))


def conda_install_numba_dev(env):
    execute("conda install -y -n {} -c numba/label/dev numba numpy"
            .format(env))


def conda_install(env, target):
    execute("conda install -y -n {} {}".format(env, target))


class NumbaIntegrationTestTarget(object):
    @property
    def name(self):
        raise NotImplementedError

    @property
    def clone_url(self):
        raise NotImplementedError

    @property
    def target_tag(self):
        raise NotImplementedError

    @property
    def conda_dependencies(self):
        raise NotImplementedError

    def install(self):
        raise NotImplementedError

    def run_tests(self):
        raise NotImplementedError

    @property
    def needs_clone(self):
        try:
            self.clone_url
        except NotImplementedError:
            return False
        else:
            return True

    @property
    def needs_checkout(self):
        try:
            self.target_tag
        except NotImplementedError:
            return False
        else:
            return True


class UmapTests(NumbaIntegrationTestTarget):
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


class HpatTests(NumbaIntegrationTestTarget):
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


class LibrosaTests(NumbaIntegrationTestTarget):
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
            "-c conda-forge ffmpeg",
        ]

    def install(self):
        execute("pip install --pre -e .[tests]")

    def run_tests(self):
        execute("pytest")


class CliffordTests(NumbaIntegrationTestTarget):

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


class AwkwardTests(NumbaIntegrationTestTarget):
    @property
    def name(self):
        return "awkward-array"

    @property
    def clone_url(self):
        return "https://github.com/scikit-hep/awkward-array"

    @property
    def target_tag(self):
        return list(git_ls_remote_tags(self.clone_url))[-1]

    @property
    def conda_dependencies(self):
        return ["numpy pytest"]

    def install(self):
        execute("python setup.py install")
        os.chdir("awkward-numba")
        execute("python setup.py install")
        os.chdir("..")

    def run_tests(self):
        execute("pytest tests/test_numba.py")   # only the test that uses Numba


def bootstrap_miniconda():
    url = miniconda_url()
    if not os.path.exists(MINCONDA_INSTALLER):
        wget_conda(url, MINCONDA_INSTALLER)
    if not os.path.exists(MINCONDA_FULL_PATH):
        install_miniconda(MINCONDA_FULL_PATH)
    inject_conda_path()
    conda_update_conda()


def setup_git(target):
    if target.needs_clone:
        if not os.path.exists(target.name):
            git_clone_tag(target.clone_url, target.target_tag)
        os.chdir(target.name)


def setup_environment(target):
    if target.name not in conda_environments():
        conda_create_env(target.name)
        conda_install_numba_dev(target.name)
        for dep in target.conda_dependencies:
            conda_install(target.name, dep)


def switch_environment(target):
    switch_environment_path(target.name)


def print_environment_details(target):
    execute("conda env export -n {}".format(target.name))
    execute("numba -s")


def find_all_targets():
    return [
        obj()
        for name, obj in inspect.getmembers(sys.modules[__name__])
        if inspect.isclass(obj)
        and issubclass(obj, NumbaIntegrationTestTarget)
        and obj is not NumbaIntegrationTestTarget
    ]


AVAILABLE_TARGETS = dict(
    (target.name, target) for target in find_all_targets()
)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--stages",
        nargs="*",
        type=str,
        choices=ALL_STAGES,
        default=ALL_STAGES,
        metavar="STAGE",
    )
    parser.add_argument(
        "-t",
        "--targets",
        nargs="*",
        type=str,
        choices=list(AVAILABLE_TARGETS.keys()),
        default=list(AVAILABLE_TARGETS.keys()),
        metavar="TARGET",
    )
    return parser.parse_args()


def main(stages, targets):
    failed = []
    basedir = os.getcwd()
    if STAGE_MINICONDA in stages:
        bootstrap_miniconda()
    else:
        inject_conda_path()
    for name, target in AVAILABLE_TARGETS.items():
        if name in targets:
            os.chdir(basedir)
            if STAGE_CLONE in stages:
                setup_git(target)
            if STAGE_ENVIRONMENT in stages:
                setup_environment(target)
            switch_environment(target)
            if STAGE_INSTALL in stages:
                target.install()
            print_environment_details(target)
            if STAGE_TESTS in stages:
                try:
                    target.run_tests()
                except subprocess.CalledProcessError:
                    failed.append(target.name)
    if STAGE_TESTS in stages:
        if failed:
            echo("The following tests failed: '{}'".format(failed))
            sys.exit(23)
        else:
            echo("All integration tests successful")


if __name__ == "__main__":
    args = parse_arguments()
    echo("stages are: '{}'".format(args.stages))
    echo("targets are: '{}'".format(args.targets))
    main(args.stages, args.targets)
