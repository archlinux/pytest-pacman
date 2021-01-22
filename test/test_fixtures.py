#!/usr/bin/python

import json
import os
import os.path

import pytest


pytest_plugins = "pytest_pacman.plugin"


@pytest.fixture(scope="session")
def core_data():
    curpath = os.path.dirname(os.path.realpath(__file__))
    return json.load(open(f'{curpath}/core.json'))


@pytest.fixture
def localdb(core_data, generate_localdb):
    return generate_localdb(core_data)


@pytest.fixture
def localdb_tmpdir(tmpdir_factory, core_data, generate_localdb):
    dbpath = str(tmpdir_factory.mktemp('dbpath'))
    return generate_localdb(core_data, dbpath)


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
