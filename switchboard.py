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
ALL_STAGES = [STAGE_MINICONDA,
              STAGE_CLONE,
              STAGE_ENVIRONMENT,
              STAGE_INSTALL,
              STAGE_TESTS,
              ]


PREFIX = "::>>"


def echo(value):
    print("{} {}".format(PREFIX, value))


def execute(command):
    echo("running: '{}'".format(command))
    return subprocess.check_output(shlex.split(command))


UNAME = execute('uname').strip().decode('utf-8')


def miniconda_url():
    if UNAME == "Linux":
        filename = MINCONDA_FILE_TEMPLATE.format(LINUX_X86_64)
    elif UNAME == "Darwin":
        filename = MINCONDA_FILE_TEMPLATE.format(MACOSX_X86_64)
    else:
        raise ValueError("Unsupported OS")
    return MINICONDA_BASE_URL + filename


def wget_conda(url):
    execute("wget {} -O miniconda.sh".format(url))


def install_miniconda(install_path):
    execute("bash miniconda.sh -b -p {}".format(install_path))


def inject_conda_path(miniconda_path):
    os.environ["PATH"] = ":".join([MINCONDA_BIN_PATH, MINCONDA_CONDABIN_PATH] +
                                  os.environ["PATH"].split(":"))


def conda_switch_environment(env):
    os.environ["PATH"] = ":".join(
        [os.path.join(conda_environments()[env], "bin")] +
        os.environ["PATH"].split(":")[1:]
    )


def git_clone(url):
    execute("git clone {}".format(url))


def git_checkout(tag):
    execute("git checkout {}".format(tag))


def conda_update_conda():
    execute("conda update -y -n base -c defaults conda")


def conda_environments():
    return dict(((os.path.basename(i), i)
                 for i in json.loads(execute(
                     "conda env list --json"))["envs"]))


def conda_create_env(name):
    execute("conda create -y -n {}".format(name))


def conda_install_numba_dev(env):
    execute("conda install -y -n {} -c numba/label/dev numba".format(env))


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
        return "0.3.8"

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
        return ["pyspark openjdk scipy",
                "-c ehsantn h5py",
                ]

    def install(self):
        conda_install(self.name,
                      "-c ehsantn "
                      "-c anaconda "
                      "-c conda-forge "
                      "hpat")

    def run_tests(self):
        execute("python -m hpat.tests.gen_test_data")
        execute("python -m hpat.runtests")


def bootstrap_miniconda():
    url = miniconda_url()
    if not os.path.exists(MINCONDA_INSTALLER):
        wget_conda(url)
    if not os.path.exists(MINCONDA_FULL_PATH):
        install_miniconda(MINCONDA_FULL_PATH)
    inject_conda_path(MINCONDA_BIN_PATH)
    conda_update_conda()


def setup_git(project):
    if project.needs_clone:
        if not os.path.exists(project.name):
            git_clone(project.clone_url)
        os.chdir(project.name)
    if project.needs_checkout:
        git_checkout(project.target_tag)


def setup_environment(project):
    if project.name not in conda_environments():
        conda_create_env(project.name)
        conda_install_numba_dev(project.name)
        for dep in project.conda_dependencies:
            conda_install(project.name, dep)


def switch_environment(target):
    conda_switch_environment(target.name)


def find_all_targets():
    return [obj() for name, obj in inspect.getmembers(sys.modules[__name__])
            if inspect.isclass(obj)
            and issubclass(obj, NumbaIntegrationTestTarget)
            and obj is not NumbaIntegrationTestTarget
            ]


available_targets = dict((target.name, target)
                         for target in find_all_targets())


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stages",
                        nargs="*",
                        type=str,
                        choices=ALL_STAGES,
                        default=ALL_STAGES,
                        metavar="STAGE")
    parser.add_argument("-t", "--targets",
                        nargs="*",
                        type=str,
                        choices=list(available_targets.keys()),
                        default=list(available_targets.keys()),
                        metavar="TARGET")
    return parser.parse_args()


def main(stages, targets):
    failed = []
    basedir = os.getcwd()
    if STAGE_MINICONDA in stages:
        bootstrap_miniconda()
    else:
        inject_conda_path(MINCONDA_BIN_PATH)
    for name, target in available_targets.items():
        if name in targets:
            os.chdir(basedir)
            if STAGE_CLONE in stages:
                setup_git(target)
            if STAGE_ENVIRONMENT in stages:
                setup_environment(target)
            switch_environment(target)
            if STAGE_INSTALL in stages:
                target.install()
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
