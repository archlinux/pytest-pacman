#!/usr/bin/python3

from collections.abc import Callable
import io
import os
import tarfile
from pathlib import Path
from typing import TypedDict

import pytest

ALPM_DB_VERSION = "9"

class PkgInfo(TypedDict):
    pkgname: str
    pkgbase: str
    xdata: str
    pkgver: str
    pkgdesc: str
    url: str
    builddate: int
    packager: str
    size: int
    arch: str
    license: list[str]
    replaces: list[str]
    group: str
    conflict: str
    provides: list[str]
    backup: list[str]
    depend: list[str]
    optdepend: list[str]
    checkdepend: list[str]


class PackageDesc(TypedDict):
    filename: str
    name: str
    base: str
    version: str
    desc: str
    csize: int
    size: int
    sha256sum: str
    pgpsig: str
    url: str
    license: list[str]
    arch: str
    builddate: int
    packager: str
    depends: list[str]
    makedepends: list[str]
    checkdepends: list[str]

    files: list[str]
    backup: list[str]


def _generate_pkginfo(data: PkgInfo) -> str:
    pkginfo = ""

    for key, value in data.items():
        if not isinstance(value, list):
            value = [value]

        for val in value:
            pkginfo += f"{key} = {val}\n"

    return pkginfo


def _generate_desc(pkg: PackageDesc) -> str:
    """ """

    desc = ""

    for key, value in pkg.items():
        # Ignore files specific keys
        if key in ["backup", "files"]:
            continue

        if not isinstance(value, list):
            value = [value]

        if not value:
            continue

        desc += f"%{key.upper()}%\n"

        for val in value:
            desc += f"{val}\n\n"

    return desc


def _generate_files(pkg: PackageDesc) -> str:
    files = ""

    if "files" in pkg:
        files += "%FILES%\n"
        for entry in pkg["files"]:
            files += f"{entry}\n"

    if "backup" in pkg:
        files += "\n"
        files += "%BACKUP%\n"
        for entry in pkg["backup"]:
            files += f"{entry}\n"

    return files


# TODO: generate files db
@pytest.fixture(scope="session")
def generate_syncdb(tmp_path_factory: pytest.TempPathFactory) -> Callable[[list[PackageDesc], str, Path], Path]:
    """Generates a sync database in a provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbname (string): sync database name (standard 'test.db')
    dbloc (string): location where sync database will be created (optional)

    Returns:
    Path: path to dbroot for when dbroot is not provided
    """

    def _generate_syncdb(pkgs: list[PackageDesc], dbname: str = "test.db", dbloc: Path | None = None) -> Path:
        if not dbloc:
            dbloc = tmp_path_factory.mktemp("dbpath") / dbname
        else:
            dbloc = dbloc / dbname

        tar = tarfile.open(dbloc, "w")
        for pkg in pkgs:
            info = tarfile.TarInfo(f"{pkg['name']}-{pkg['version']}/desc")
            data = _generate_desc(pkg)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data.encode()))

        return dbloc

    return _generate_syncdb


@pytest.fixture(scope="session")
def generate_localdb(tmp_path_factory: pytest.TempPathFactory) -> Callable[[list[PackageDesc], Path | None, str], Path]:
    """Generates a localdb in provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbroot (string): the path to the root (normally /var/lib/pacman)
    alpm_db_version (string): the ALPM_DB_VERSION (default 9)

    Returns:
    Path: path to dbroot for when dbroot is not provided
    """

    def _generate_localdb(pkgs: list[PackageDesc], dbroot: Path | None = None,
                          alpm_db_version: str = ALPM_DB_VERSION) -> Path:
        if dbroot is None:
            dbroot = tmp_path_factory.mktemp("dbpath")

        dbloc = f"{dbroot}/local"
        os.mkdir(dbloc)

        with open(f"{dbloc}/ALPM_DB_VERSION", "w") as fp:
            fp.write(alpm_db_version)

        for pkg in pkgs:
            path = f"{dbloc}/{pkg['name']}-{pkg['version']}"
            os.makedirs(path)

            with open(f"{path}/desc", "w") as f:
                f.write(_generate_desc(pkg))

            if "backup" in pkg or "files" in pkg:
                with open(f"{path}/files", "w") as f:
                    f.write(_generate_files(pkg))

        return dbroot

    return _generate_localdb


@pytest.fixture(scope="session")
def generate_package(tmp_path_factory: pytest.TempPathFactory)-> Callable[[PkgInfo, str, Path | None], Path]:
    """Generates a package in provided location or when not provided pytest tmpdir

    Parameters:
    data (object): a dict containing the fields for PKGINFO
    pkgname (string): the package file name ($pkgname-$pkgver-$pkgrel.pkg.tar)
    pkgpath (string): the path to save the pkg file

    Returns:
    Path: path to package
    """

    def _generate_package(data: PkgInfo, pkgname: str = "test.pkg.tar", pkgpath: Path | None = None) -> Path:
        if pkgpath is None:
            pkgpath = tmp_path_factory.mktemp("pkgpath") / pkgname
        else:
            pkgpath = pkgpath / pkgname

        tar = tarfile.open(pkgpath, "w")
        info = tarfile.TarInfo(".PKGINFO")
        pkginfo = _generate_pkginfo(data)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(pkginfo.encode()))

        return pkgpath

    return _generate_package
