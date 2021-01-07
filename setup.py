#!/usr/bin/env python
"""setuptools configuration.

See:  https://python-packaging.readthedocs.io/en/latest/index.html
"""
from setuptools import setup


def readme():
    """Load README.rst."""
    with open("README.rst", "r") as file:
        return file.read()


setup(
    name="pccc",
    version="0.2.0",
    description="Python Conventional Commit Checker",
    long_description=readme(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    url="https://github.com/jeremyagray/pccc",
    author="Jeremy A Gray",
    author_email="jeremy.a.gray@gmail.com",
    license="GPL-3.0-or-later",
    packages=["pccc"],
    entry_points={
        "console_scripts": ["pccc=pccc.cli:main"],
    },
    install_requires=[
        "pyparsing",
        "toml",
    ],
    tests_require=[
        "pytest",
        "pytest-black",
        "pytest-flake8",
        "pytest-pydocstyle",
    ],
)
