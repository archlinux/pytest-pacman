#!/usr/bin/python

import json
import tarfile
import os
import os.path

import pytest


pytest_plugins = "pytest_pacman.plugin"


@pytest.fixture(scope="session")
def core_data():
    curpath = os.path.dirname(os.path.realpath(__file__))
    return json.load(open(f"{curpath}/core.json"))


@pytest.fixture()
def localdb(core_data, generate_localdb):
    return generate_localdb(core_data)


@pytest.fixture()
def localdb_tmpdir(tmpdir_factory, core_data, generate_localdb):
    dbpath = str(tmpdir_factory.mktemp("dbpath"))
    return generate_localdb(core_data, dbpath)


@pytest.fixture()
def syncdb(core_data, generate_syncdb):
    return generate_syncdb(core_data)


@pytest.fixture()
def syncdb_tmpdir(tmpdir_factory, core_data, generate_syncdb):
    dbpath = str(tmpdir_factory.mktemp("dbpath"))
    return generate_syncdb(core_data, "foo.db", dbpath)


@pytest.fixture(scope="session")
def pkg_data():
    curpath = os.path.dirname(os.path.realpath(__file__))
    return json.load(open(f"{curpath}/package.json"))


@pytest.fixture()
def package(pkg_data, generate_package):
    return generate_package(pkg_data)


@pytest.fixture()
def package_tmpdir(tmpdir_factory, pkg_data, generate_package):
    pkgpath = str(tmpdir_factory.mktemp("pkg"))
    return generate_package(pkg_data, pkgpath=pkgpath)


def test_localdb(core_data, localdb):
    pkg = core_data[0]
    pkgpath = f"{localdb}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(localdb)
    assert os.path.exists(pkgpath)
    assert os.path.exists(f"{pkgpath}/desc")

    pkg = core_data[-1]
    pkgpath = f"{localdb}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(f"{pkgpath}/files")
    assert os.path.exists(f"{pkgpath}/desc")


def test_localdb_tmpdir(core_data, localdb_tmpdir):
    pkg = core_data[0]
    pkgpath = f"{localdb_tmpdir}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(localdb_tmpdir)
    assert os.path.exists(pkgpath)


def test_syncdb(core_data, syncdb):
    with tarfile.open(syncdb) as tar:
        for index, tarinfo in enumerate(tar):
            pkg = core_data[index]
            pkgpath = f"{pkg['name']}-{pkg['version']}"

            assert tarinfo.name == f"{pkgpath}/desc"


def test_syncdb_tmpdir(core_data, syncdb_tmpdir):
    with tarfile.open(syncdb_tmpdir) as tar:
        for index, tarinfo in enumerate(tar):
            pkg = core_data[index]
            pkgpath = f"{pkg['name']}-{pkg['version']}"

            assert tarinfo.name == f"{pkgpath}/desc"


def test_package(pkg_data, package):
    with tarfile.open(package) as tar:
        for _, tarinfo in enumerate(tar):
            assert tarinfo.name == ".PKGINFO"


def test_package_tmpdir(pkg_data, package_tmpdir):
    with tarfile.open(package_tmpdir) as tar:
        for _, tarinfo in enumerate(tar):
            assert tarinfo.name == ".PKGINFO"
