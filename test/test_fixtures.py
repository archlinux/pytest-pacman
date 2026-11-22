#!/usr/bin/python

import gzip
import hashlib
import tarfile
import os
import os.path
from pathlib import Path
from typing import Literal

import pytest

from pytest_pacman.plugin import GenerateLocalDb, GeneratePackage, GenerateSyncDb, PackageDesc, PkgFile, PkgInfo


pytest_plugins = "pytest_pacman.plugin"

PKG_FILES: dict[str, PkgFile] = {
    "srv/ftp": {"type": "dir", "mode": 0o555, "gid": 11},
    "usr/bin/foo": {"type": "file", "content": b"#!/bin/sh\n", "mode": 0o755},
    "usr/lib/libfoo.so": {"type": "link", "target": "libfoo.so.1"},
    "usr/lib/libfoo.so.1": {"type": "link", "target": "libfoo.so.1.0"},
    "usr/lib/libfoo.so.1.0": {"type": "file", "content": b"\x7fELF"},
}


@pytest.fixture(scope="session")
def core_data() -> list[PackageDesc]:
    return [
        {
            "name": "linux",
            "base": "linux",
            "version": "5.5.3.arch1-1",
            "desc": "The linux kernel and modules",
            "url": "https://kernel.org",
            "license": ["GPL2"],
            "arch": "x86_64",
            "builddate": 1573556456,
            "packager": "Arch Dev <developer@archlinux.org>",
            "csize": 2483776,
            "depends": ["coreutils"],
            "makedepends": ["bc"],
            "optdepends": ["linux-firmware"],
        },
        {
            "name": "git",
            "base": "git",
            "version": "2.25.0-1",
            "desc": "the fast distributed version control system",
            "url": "https://git-scm.com/",
            "license": ["GPL2"],
            "arch": "x86_64",
            "builddate": 1573556456,
            "packager": "Arch Git <archdev@archlinux.org>",
            "csize": 2483776,
            "groups": ["base-devel"],
        },
        {
            "name": "pacman",
            "base": "pacman",
            "version": "5.0-1",
            "desc": "A library-based package manager with dependency support",
            "url": "https://archlinux.org/pacman",
            "license": ["GPL"],
            "arch": "x86_64",
            "builddate": 1573556451,
            "packager": "Arch Dev <developer@archlinux.org>",
            "depends": ["bash", "glibc", "libarchive"],
            "groups": ["base-devel"],
            "backup": [
                "etc/pacman.conf\t9dd54ec11513b2838bffb04dab66c50a",
                "etc/makepkg.conf\tf613f9ecbfcafdaed423848ba7190b61",
            ],
            "files": ["etc/", "etc/pacman.conf", "var/", "var/lib/", "var/lib/pacman"],
        },
    ]


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
    return {
        "pkgname": "filesystem",
        "pkgbase": "filesystem",
        "pkgver": "1-1",
        "pkgdesc": "filesystem",
        "url": "https://archlinux.org",
        "builddate": 1599085821,
        "packager": "Test <test@archlinux.org>",
        "arch": "x86_64",
        "size": 0,
        "license": ["GPL"],
        "depend": ["iana-etc", "vi"],
    }


@pytest.fixture
def package(pkg_data: PkgInfo, generate_package: GeneratePackage) -> Path:
    return generate_package(pkg_data)


@pytest.fixture
def package_tmpdir(
    tmp_path_factory: pytest.TempPathFactory, pkg_data: PkgInfo, generate_package: GeneratePackage
) -> Path:
    pkgpath = tmp_path_factory.mktemp("pkg")
    return generate_package(pkg_data, pkgpath=pkgpath)


@pytest.fixture
def package_files(pkg_data: PkgInfo, generate_package: GeneratePackage) -> Path:
    return generate_package(pkg_data, files=PKG_FILES)


def _read(tar: tarfile.TarFile, name: str) -> bytes:
    fp = tar.extractfile(name)
    assert fp is not None
    return fp.read()


def _parse_mtree(data: bytes) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    defaults: dict[str, str] = {}
    for line in gzip.decompress(data).decode().splitlines():
        if not line or line.startswith("#"):
            continue

        keyword, *attrs = line.split()
        values = dict(attr.split("=", 1) for attr in attrs)

        if keyword == "/set":
            defaults.update(values)
        else:
            entries[keyword.removeprefix("./")] = defaults | values

    return entries


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


def test_localdb_desc(core_data: list[PackageDesc], localdb: Path) -> None:
    pkg = core_data[1]
    with open(f"{localdb}/local/{pkg['name']}-{pkg['version']}/desc") as fp:
        desc = fp.read()

    assert desc == (
        "%NAME%\ngit\n\n"
        "%BASE%\ngit\n\n"
        "%VERSION%\n2.25.0-1\n\n"
        "%DESC%\nthe fast distributed version control system\n\n"
        "%URL%\nhttps://git-scm.com/\n\n"
        "%LICENSE%\nGPL2\n\n"
        "%ARCH%\nx86_64\n\n"
        "%BUILDDATE%\n1573556456\n\n"
        "%PACKAGER%\nArch Git <archdev@archlinux.org>\n\n"
        "%GROUPS%\nbase-devel\n\n"
    )


def test_syncdb_desc_csize(core_data: list[PackageDesc], syncdb: Path) -> None:
    pkg = core_data[1]
    with tarfile.open(syncdb) as tar:
        desc = _read(tar, f"{pkg['name']}-{pkg['version']}/desc").decode()

    assert "%CSIZE%\n2483776\n\n" in desc


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
        assert tar.getnames() == [".MTREE", ".PKGINFO"]


def test_package_tmpdir(pkg_data: PkgInfo, package_tmpdir: Path) -> None:
    with tarfile.open(package_tmpdir) as tar:
        assert tar.getnames() == [".MTREE", ".PKGINFO"]


def test_package_files(pkg_data: PkgInfo, package_files: Path) -> None:
    with tarfile.open(package_files) as tar:
        names = tar.getnames()
        members = {m.name: m for m in tar.getmembers()}
        foo = _read(tar, "usr/bin/foo")
        libfoo = _read(tar, "usr/lib/libfoo.so.1.0")

    assert names[:2] == [".MTREE", ".PKGINFO"]
    assert names[2:] == sorted(names[2:])
    assert set(names[2:]) == {
        "srv",
        "srv/ftp",
        "usr",
        "usr/bin",
        "usr/bin/foo",
        "usr/lib",
        "usr/lib/libfoo.so",
        "usr/lib/libfoo.so.1",
        "usr/lib/libfoo.so.1.0",
    }

    for parent in ("srv", "usr", "usr/bin", "usr/lib"):
        assert members[parent].isdir()
        assert members[parent].mode == 0o755

    assert members["srv/ftp"].isdir()
    assert members["srv/ftp"].mode == 0o555
    assert members["srv/ftp"].gid == 11

    assert members["usr/bin/foo"].isfile()
    assert members["usr/bin/foo"].mode == 0o755
    assert foo == b"#!/bin/sh\n"

    assert members["usr/lib/libfoo.so.1.0"].isfile()
    assert members["usr/lib/libfoo.so.1.0"].mode == 0o644
    assert libfoo == b"\x7fELF"

    assert members["usr/lib/libfoo.so"].issym()
    assert members["usr/lib/libfoo.so"].linkname == "libfoo.so.1"
    assert members["usr/lib/libfoo.so.1"].issym()
    assert members["usr/lib/libfoo.so.1"].linkname == "libfoo.so.1.0"

    for member in members.values():
        assert member.uid == 0
        assert member.mtime == pkg_data["builddate"]


def test_package_files_mtree(pkg_data: PkgInfo, package_files: Path) -> None:
    with tarfile.open(package_files) as tar:
        names = tar.getnames()
        mtree = _parse_mtree(_read(tar, ".MTREE"))
        pkginfo = _read(tar, ".PKGINFO")

    assert set(mtree) == set(names) - {".MTREE"}
    for entry in mtree.values():
        assert entry["time"] == f"{pkg_data['builddate']}.0"
        assert entry["uid"] == "0"

    assert mtree[".PKGINFO"]["size"] == str(len(pkginfo))
    assert mtree[".PKGINFO"]["sha256digest"] == hashlib.sha256(pkginfo).hexdigest()

    foo = mtree["usr/bin/foo"]
    assert foo["type"] == "file"
    assert int(foo["mode"], 8) == 0o755
    assert foo["size"] == "10"
    assert foo["sha256digest"] == hashlib.sha256(b"#!/bin/sh\n").hexdigest()

    assert mtree["usr/lib/libfoo.so"]["type"] == "link"
    assert mtree["usr/lib/libfoo.so"]["link"] == "libfoo.so.1"

    assert mtree["srv/ftp"]["type"] == "dir"
    assert int(mtree["srv/ftp"]["mode"], 8) == 0o555
    assert mtree["srv/ftp"]["gid"] == "11"


@pytest.mark.parametrize(
    ("pkgname", "mode"),
    [
        ("test.pkg.tar", "r:"),
        ("test.pkg.tar.gz", "r:gz"),
        ("test.pkg.tar.bz2", "r:bz2"),
        ("test.pkg.tar.xz", "r:xz"),
        ("test.pkg.tar.zst", "r:zst"),
    ],
)
def test_package_compression(
    pkg_data: PkgInfo,
    generate_package: GeneratePackage,
    pkgname: str,
    mode: Literal["r:", "r:gz", "r:bz2", "r:xz", "r:zst"],
) -> None:
    pkg = generate_package(pkg_data, pkgname=pkgname, files=PKG_FILES)
    assert pkg.name == pkgname

    with tarfile.open(pkg, mode) as tar:
        assert tar.getnames()[:2] == [".MTREE", ".PKGINFO"]
        assert _read(tar, "usr/bin/foo") == b"#!/bin/sh\n"


@pytest.mark.parametrize("ext", [".lz4", ".lzo", ".lrz", ".lz", ".Z", ".foobar"])
def test_package_compression_unsupported(pkg_data: PkgInfo, generate_package: GeneratePackage, ext: str) -> None:
    with pytest.raises(ValueError, match="unsupported compression"):
        generate_package(pkg_data, pkgname=f"test.pkg.tar{ext}")


def test_package_link_without_target(tmp_path: Path, pkg_data: PkgInfo, generate_package: GeneratePackage) -> None:
    with pytest.raises(ValueError, match="type 'link' requires 'target' to be set"):
        generate_package(pkg_data, pkgpath=tmp_path, files={"usr/lib/libfoo.so": {"type": "link"}})

    assert not (tmp_path / "test.pkg.tar").exists()
