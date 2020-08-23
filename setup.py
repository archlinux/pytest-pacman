"""Setuptools install script for pytest-pacman."""

import io

from setuptools import setup

with io.open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="pytest-pacman",
    description="py.test plugin to generate pacman db fixtures",
    long_description=long_description,
    version="0.1",
    author="Jelle van der Waa",
    author_email="jelle@archlinux.org",
    url="http://github.com/archlinux/pytest-pacman/",
    license="MIT",
    packages=["pytest_pacman"],
    entry_points={"pytest11": ["pacman = pytest_pacman.plugin"]},
    install_requires=["pytest>=3.6.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: DFSG approved",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Testing",
    ],
)
