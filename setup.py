import distutils.cmd
import distutils.log
import os
import subprocess

from setuptools import find_packages, setup

from coloredmanga_downloader import DESCRIPTION, SCRIPT_NAME, SCRIPT_VERSION
INPUT_FILE = "coloredmanga_downloader.py"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class LintCommand(distutils.cmd.Command):
    """Lint with flake8."""

    description = "run flake8 on source files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self) -> bool:
        self.announce("Linting...", level=distutils.log.WARN)

        self.announce("flake8 pass...", level=distutils.log.WARN)
        return subprocess.run(["flake8", INPUT_FILE]).returncode == 0


class FormatCommand(distutils.cmd.Command):
    """Format with black."""

    description = "Run isort and black on source files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self) -> bool:
        self.announce("Formatting...", level=distutils.log.WARN)

        self.announce("isort pass...", level=distutils.log.WARN)
        if subprocess.run(["isort", "-rc", "--atomic", INPUT_FILE]).returncode != 0:
            return False

        self.announce("black pass...", level=distutils.log.WARN)
        return subprocess.run(
            [
                "black",
                "--target-version",
                "py38",
                "-l",
                "120",
                INPUT_FILE,
            ],
        ).returncode == 0


setup(
    name=SCRIPT_NAME,
    version=SCRIPT_VERSION,
    author="FloZone",
    description=DESCRIPTION,
    long_description=read("README.md"),
    packages=find_packages(),
    cmdclass={
        "lint": LintCommand,
        "fmt": FormatCommand,
    },
)
