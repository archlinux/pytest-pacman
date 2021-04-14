#!/usr/bin/python3

import io
import os
import tarfile

import pytest

ALPM_DB_VERSION = '9'


def _generate_pkginfo(data):
    pkginfo = ''

    for key, value in data.items():
        if not isinstance(value, list):
            value = [value]

        for val in value:
            pkginfo += f'{key} = {val}\n'

    return pkginfo


def _generate_desc(pkg):
    '''
    '''

    desc = ""

    for key, value in pkg.items():
        # Ignore files specific keys
        if key in ['backup', 'files']:
            continue

        if not isinstance(value, list):
            value = [value]

        if not value:
            continue

        desc += f"%{key.upper()}%\n"

        for val in value:
            desc += f"{val}\n\n"

    return desc


def _generate_files(pkg):
    files = ""

    if 'files' in pkg:
        files += "%FILES%\n"
        for entry in pkg['files']:
            files += f'{entry}\n'

    if 'backup' in pkg:
        files += '\n'
        files += "%BACKUP%\n"
        for entry in pkg['backup']:
            files += f'{entry}\n'

    return files


# TODO: generate files db
@pytest.fixture(scope="session")
def generate_syncdb(tmpdir_factory):
    '''Generates a sync database in a provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbname (string): sync database name (standard 'test.db')
    dbloc (string): location where sync database will be created (optional)

    Returns:
    str: path to dbroot for when dbroot is not provided
    '''

    def _generate_syncdb(pkgs, dbname='test.db', dbloc=''):
        if not dbloc:
            dbloc = str(tmpdir_factory.mktemp('dbpath').join(dbname))
        else:
            dbloc = os.path.join(dbloc, dbname)

        tar = tarfile.open(dbloc, "w")
        for pkg in pkgs:
            info = tarfile.TarInfo(f"{pkg['name']}-{pkg['version']}/desc")
            data = _generate_desc(pkg)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data.encode()))

        return dbloc

    return _generate_syncdb


@pytest.fixture(scope="session")
def generate_localdb(tmpdir_factory):
    '''Generates a localdb in provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbroot (string): the path to the root (normally /var/lib/pacman)
    alpm_db_version (string): the ALPM_DB_VERSION (default 9)

    Returns:
    str: path to dbroot for when dbroot is not provided
    '''

    def _generate_localdb(pkgs, dbroot='', alpm_db_version=ALPM_DB_VERSION):
        if not dbroot:
            dbroot = str(tmpdir_factory.mktemp('dbpath'))

        dbloc = f"{dbroot}/local"
        os.mkdir(dbloc)

        with open(f"{dbloc}/ALPM_DB_VERSION", 'w') as fp:
            fp.write(ALPM_DB_VERSION)

        for pkg in pkgs:
            path = f"{dbloc}/{pkg['name']}-{pkg['version']}"
            os.makedirs(path)

            with open(f'{path}/desc', 'w') as f:
                f.write(_generate_desc(pkg))

            if 'backup' in pkg or 'files' in pkg:
                with open(f'{path}/files', 'w') as f:
                    f.write(_generate_files(pkg))

        return dbroot

    return _generate_localdb


@pytest.fixture(scope="session")
def generate_package(tmpdir_factory):
    '''Generates a package in provided location or when not provided pytest tmpdir

    Parameters:
    data (object): a dict containing the fields for PKGINFO
    pkgname (string): the package file name ($pkgname-$pkgver-$pkgrel.pkg.tar)
    pkgpath (string): the path to save the pkg file

    Returns:
    str: path to package
    '''

    def _generate_package(data, pkgname='test.pkg.tar', pkgpath=''):
        if not pkgpath:
            pkgpath = str(tmpdir_factory.mktemp('pkgpath').join(pkgname))
        else:
            pkgpath = os.path.join(pkgpath, pkgname)

        tar = tarfile.open(pkgpath, 'w')
        info = tarfile.TarInfo('.PKGINFO')
        data = _generate_pkginfo(data)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data.encode()))

        return pkgpath

    return _generate_package
