#!/usr/bin/python3

import os
import tarfile

from shutil import rmtree
from tempfile import mkdtemp

import pytest


def generate_desc(pkg):
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


def generate_files(pkg):
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


def generate_syncdb(pkgs, dbfile):
    dbpath = mkdtemp(dir='/tmp')

    # TODO: refactor to not use chdir.
    cwd = os.getcwd()
    os.chdir(dbpath)

    with tarfile.open(dbfile, "w") as tar:
        for pkg in pkgs:
            path = f"{pkg['name']}-{pkg['version']}"
            os.makedirs(path)

            with open(f'{path}/desc', 'w') as f:
                f.write(generate_desc(pkg))

            tar.add(path)

    rmtree(dbpath)
    os.chdir(cwd)


@pytest.fixture(scope="session")
def generate_localdb(tmpdir_factory):
    '''Generates a localdb in provided location or when not provided pytest tmpdir

    Parameters:
    pkgs (list): a list of dicts containing
    dbroot (string): the path to the root (normally /var/lib/pacman)

    Returns:
    str: path to dbroot for when dbroot is not provided
    '''

    def _generate_localdb(pkgs, dbroot=''):
        if not dbroot:
            dbroot = str(tmpdir_factory.mktemp('dbpath'))

        dbloc = f"{dbroot}/local"
        os.mkdir(dbloc)

        for pkg in pkgs[:1]:
            path = f"{dbloc}/{pkg['name']}-{pkg['version']}"
            os.makedirs(path)

            with open(f'{path}/desc', 'w') as f:
                f.write(generate_desc(pkg))

            if 'backup' in pkg or 'files' in pkg:
                with open(f'{path}/files', 'w') as f:
                    f.write(generate_files(pkg))

        return dbroot

    return _generate_localdb
