#!/usr/bin/env python

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


def execute(command):
    print(command)
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
    print(project.needs_clone)
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


targets = dict((target.name, target) for target in find_all_targets())


if __name__ == "__main__":
    basedir = os.getcwd()
    bootstrap_miniconda()
    for name, target in targets.items():
        if name == 'umap':
            continue
        os.chdir(basedir)
        setup_git(target)
        setup_environment(target)
        switch_environment(target)
        target.install()
        target.run_tests()
