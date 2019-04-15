import os
import shlex
import subprocess

MINICONDA_BASE_URL = "https://repo.continuum.io/miniconda/"
MINCONDA_FILE_TEMPLATE = "Miniconda3-latest-{}.sh"
MINCONDA_INSTALLER = "miniconda.sh"
MINCONDA_PATH = "miniconda3"
MINCONDA_FULL_PATH = os.path.join(os.getcwd(), MINCONDA_PATH)
MINCONDA_BIN_PATH = os.path.join(MINCONDA_FULL_PATH, "bin")

LINUX_X86 = "Linux-x86"
LINUX_X86_64 = "Linux-x86_64"
MACOSX_X86_64 = "MacOSX-x86_64"


def execute(command):
    return subprocess.check_output(shlex.split(command))


def conda_url():
    uname = execute('uname').strip().decode('utf-8')
    if uname == "Linux":
        filename = MINCONDA_FILE_TEMPLATE.format(LINUX_X86)
    elif uname == "Darwin":
        filename = MINCONDA_FILE_TEMPLATE.format(MACOSX_X86_64)
    else:
        raise ValueError("Unsupported OS")
    return MINICONDA_BASE_URL + filename


def wget_conda(url):
    execute("wget {} -O miniconda.sh".format(url))


def install_miniconda(install_path):
    execute("bash miniconda.sh -b -p {}".format(install_path))


def inject_conda_path():
    os.environ["PATH"] = MINCONDA_BIN_PATH + ":" + os.environ["PATH"]
    print(os.environ["PATH"])


def create_conda_env(name):
    execute("conda create -n {}".format(name))


if __name__ == "__main__":
    url = conda_url()
    if not os.path.exists(MINCONDA_INSTALLER):
        wget_conda(url)
    if not os.path.exists(MINCONDA_FULL_PATH):
        install_miniconda(MINCONDA_FULL_PATH)
    inject_conda_path()
    create_conda_env("TEST")
