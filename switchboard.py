import os
import shlex
import subprocess
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


def conda_url():
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
    old = os.environ["PATH"].split(":")
    env_bin_path = os.path.join(conda_environments()[env], "bin")
    new = [env_bin_path] + old[1:]
    os.environ["PATH"] = ":".join(new)


def git_clone(url):
    execute("git clone {}".format(url))


def git_checkout(tag):
    execute("git checkout {}".format(tag))


def conda_update_conda():
    execute("conda update -y -n base -c defaults conda")


def conda_environments():
    loaded_json = json.loads(execute("conda env list --json"))["envs"]
    return dict(((os.path.basename(i), i) for i in loaded_json))


def conda_create_env(name):
    execute("conda create -y -n {}".format(name))


def conda_install_numba_dev(env):
    execute("conda install -y -n {} -c numba/label/dev numba".format(env))


def conda_install(env, target):
    execute("conda install -y -n {} {}".format(env, target))


class UmapTests(object):

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


class HpatTests(object):

    @property
    def name(self):
        return "hpat"

    @property
    def clone_url(self):
        return "https://github.com/IntelLabs/hpat"

    @property
    def target_tag(self):
        return "0.29.2"

    @property
    def conda_dependencies(self):
        return ["pyspark openjdk numpy scipy pandas boost cmake pyarrow",
                "-c conda-forge mpich mpi",
                "-c ehsantn h5py",
                ]

    def install(self):
        if UNAME == "Linux":
            conda_install(self.name,
                          "gcc_linux-64 gxx_linux-64 gfortran_linux-64")
        os.environ["HDF5_DIR"] = MINCONDA_FULL_PATH
        os.environ["CONDA_PREFIX"] = conda_environments()["hpat"]
        execute("python setup.py develop")

    def run_tests(self):
        execute("python hpat/tests/gen_test_data.py")
        execute("python -m unittest")


if __name__ == "__main__":
    basedir = os.getcwd()
    url = conda_url()
    if not os.path.exists(MINCONDA_INSTALLER):
        wget_conda(url)
    if not os.path.exists(MINCONDA_FULL_PATH):
        install_miniconda(MINCONDA_FULL_PATH)
    inject_conda_path(MINCONDA_BIN_PATH)
    conda_update_conda()
    for project in [HpatTests()]:
        if not os.path.exists(project.name):
            git_clone(project.clone_url)
        os.chdir(project.name)
        git_checkout(project.target_tag)
        if project.name not in conda_environments():
            conda_create_env(project.name)
            conda_install_numba_dev(project.name)
            for dep in project.conda_dependencies:
                conda_install(project.name, dep)

        conda_switch_environment(project.name)
        project.install()
        project.run_tests()
        os.chdir(basedir)
