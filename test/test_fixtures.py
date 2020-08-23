#!/usr/bin/python

import json
import os
import os.path

import pytest


pytest_plugins = "pytest_pacman.plugin"


@pytest.fixture
def core_data():
    curpath = os.path.dirname(os.path.realpath(__file__))
    return json.load(open(f'{curpath}/core.json'))


@pytest.fixture(scope="session")
def localdb(tmpdir_factory, core_data, generate_localdb):
    dbpath = str(tmpdir_factory.mktemp('dbpath'))
    return generate_localdb(core_data, dbpath)


def test_localdb(core_data, localdb):
    pkg = core_data[0]
    pkgpath = f"{localdb}/local/{pkg['name']}-{pkg['version']}"
    assert os.path.exists(localdb)
    assert os.path.exists(pkgpath)
