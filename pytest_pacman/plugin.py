#!/usr/bin/python3

import io
import os
import tarfile
from pathlib import Path
from typing import Protocol, Required, TypedDict

import pytest

ALPM_DB_VERSION = "9"


class PkgInfo(TypedDict, total=False):
    pkgname: Required[str]
    pkgbase: Required[str]
    pkgver: Required[str]
    pkgdesc: Required[str]
    url: Required[str]
    builddate: Required[int]
    packager: Required[str]
    size: Required[int]
    arch: Required[str]
    license: list[str]
    replaces: list[str]
    group: list[str]
    conflict: list[str]
    xdata: list[str]
    provides: list[str]
    backup: list[str]
    depend: list[str]
    makedepend: list[str]
    optdepend: list[str]
    checkdepend: list[str]


class PackageDesc(TypedDict, total=False):
    # needed to build the db entry path
    name: Required[str]
    version: Required[str]

    # common to sync and local db
    base: str
    desc: str
    url: str
    license: list[str]
    arch: str
    builddate: int
    packager: str
    groups: list[str]
    depends: list[str]
    makedepends: list[str]
    checkdepends: list[str]
    optdepends: list[str]
    provides: list[str]
    conflicts: list[str]
    replaces: list[str]

    # sync db only
    filename: str
    csize: int
    isize: int
    sha256sum: str
    md5sum: str
    pgpsig: str

    # local db only
    size: int
    installdate: int
    reason: int
    validation: list[str]
    xdata: list[str]

    # files db
    files: list[str]
    backup: list[str]


class GenerateSyncDb(Protocol):
    def __call__(self, pkgs: list[PackageDesc], dbname: str = ..., dbloc: Path | None = ...) -> Path: ...


class GenerateLocalDb(Protocol):
    def __call__(self, pkgs: list[PackageDesc], dbroot: Path | None = ..., alpm_db_version: str = ...) -> Path: ...


class GeneratePackage(Protocol):
    def __call__(self, data: PkgInfo, pkgname: str = ..., pkgpath: Path | None = ...) -> Path: ...


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
def generate_syncdb(tmp_path_factory: pytest.TempPathFactory) -> GenerateSyncDb:
    """Generates a sync database in a provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbname (string): sync database name (standard 'test.db')
    dbloc (Path): location where sync database will be created (optional)

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
def generate_localdb(tmp_path_factory: pytest.TempPathFactory) -> GenerateLocalDb:
    """Generates a localdb in provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbroot (Path): the path to the root (normally /var/lib/pacman)
    alpm_db_version (string): the ALPM_DB_VERSION (default 9)

    Returns:
    Path: path to dbroot for when dbroot is not provided
    """

    def _generate_localdb(
        pkgs: list[PackageDesc], dbroot: Path | None = None, alpm_db_version: str = ALPM_DB_VERSION
    ) -> Path:
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
def generate_package(tmp_path_factory: pytest.TempPathFactory) -> GeneratePackage:
    """Generates a package in provided location or when not provided pytest tmpdir

    Parameters:
    data (object): a dict containing the fields for PKGINFO
    pkgname (string): the package file name ($pkgname-$pkgver-$pkgrel.pkg.tar)
    pkgpath (Path): the path to save the pkg file

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
