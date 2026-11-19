#!/usr/bin/python

import json
import tarfile
import os
import os.path
from pathlib import Path
from typing import cast

import pytest

from pytest_pacman.plugin import GenerateLocalDb, GeneratePackage, GenerateSyncDb, PackageDesc, PkgInfo


pytest_plugins = "pytest_pacman.plugin"


@pytest.fixture(scope="session")
def core_data() -> list[PackageDesc]:
    curpath = os.path.dirname(os.path.realpath(__file__))
    return cast(list[PackageDesc], json.load(open(f"{curpath}/core.json")))


@pytest.fixture
def localdb(core_data: list[PackageDesc], generate_localdb: GenerateLocalDb) -> Path:
    return generate_localdb(core_data)


@pytest.fixture
def localdb_tmpdir(
    tmp_path_factory: pytest.TempPathFactory, core_data: list[PackageDesc], generate_localdb: GenerateLocalDb
) -> Path:
    dbpath = tmp_path_factory.mktemp("dbpath")
    return generate_localdb(core_data, dbpath)


@pytest.fixture
def syncdb(core_data: list[PackageDesc], generate_syncdb: GenerateSyncDb) -> Path:
    return generate_syncdb(core_data)


@pytest.fixture
def syncdb_tmpdir(
    tmp_path_factory: pytest.TempPathFactory, core_data: list[PackageDesc], generate_syncdb: GenerateSyncDb
) -> Path:
    dbpath = tmp_path_factory.mktemp("dbpath")
    return generate_syncdb(core_data, "foo.db", dbpath)


@pytest.fixture(scope="session")
def pkg_data() -> PkgInfo:
    curpath = os.path.dirname(os.path.realpath(__file__))
    return cast(PkgInfo, json.load(open(f"{curpath}/package.json")))


@pytest.fixture
def package(pkg_data: PkgInfo, generate_package: GeneratePackage) -> Path:
    return generate_package(pkg_data)


@pytest.fixture
def package_tmpdir(
    tmp_path_factory: pytest.TempPathFactory, pkg_data: PkgInfo, generate_package: GeneratePackage
) -> Path:
    pkgpath = tmp_path_factory.mktemp("pkg")
    return generate_package(pkg_data, pkgpath=pkgpath)


def test_localdb(core_data: list[PackageDesc], localdb: Path) -> None:
    pkg = core_data[0]
    pkgpath = f"{localdb}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(localdb)
    assert os.path.exists(pkgpath)
    assert os.path.exists(f"{pkgpath}/desc")

    pkg = core_data[-1]
    pkgpath = f"{localdb}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(f"{pkgpath}/files")
    assert os.path.exists(f"{pkgpath}/desc")


def test_localdb_tmpdir(core_data: list[PackageDesc], localdb_tmpdir: Path) -> None:
    pkg = core_data[0]
    pkgpath = f"{localdb_tmpdir}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(localdb_tmpdir)
    assert os.path.exists(pkgpath)


def test_syncdb(core_data: list[PackageDesc], syncdb: Path) -> None:
    with tarfile.open(syncdb) as tar:
        for index, tarinfo in enumerate(tar):
            pkg = core_data[index]
            pkgpath = f"{pkg['name']}-{pkg['version']}"

            assert tarinfo.name == f"{pkgpath}/desc"


def test_syncdb_tmpdir(core_data: list[PackageDesc], syncdb_tmpdir: Path) -> None:
    with tarfile.open(syncdb_tmpdir) as tar:
        for index, tarinfo in enumerate(tar):
            pkg = core_data[index]
            pkgpath = f"{pkg['name']}-{pkg['version']}"

            assert tarinfo.name == f"{pkgpath}/desc"


def test_package(pkg_data: PkgInfo, package: Path) -> None:
    with tarfile.open(package) as tar:
        for _, tarinfo in enumerate(tar):
            assert tarinfo.name == ".PKGINFO"


def test_package_tmpdir(pkg_data: PkgInfo, package_tmpdir: Path) -> None:
    with tarfile.open(package_tmpdir) as tar:
        for _, tarinfo in enumerate(tar):
            assert tarinfo.name == ".PKGINFO"
