.. pytest-pacman documentation master file, created by
   sphinx-quickstart on Wed Apr 14 21:20:59 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pytest-pacman documentation
===========================

This is a pytest plugin which will generate a test pacman sync, local db and a
pacman package. To be used in pyalpm, archweb and arch-signoff for testing.


Basic Usage
-----------

.. code-block:: python

        from pyalpm import Handle  

        @pytest.fixture(scope="session")
        def empty_localdb(generate_localdb):
                return generate_localdb([])


        def test_handle(empty_localdb):
                handle = Handle("/", empty_localdb)
                localdb = handle.get_localdb()

        @pytest.fixture(scope="session")
        def empty_localdb(generate_localdb):
                return generate_localdb([])

        @pytest.fixture(scope="session")
        def db_data():
                return [{
                        "name": "linux-firmware",
                        "base": "linux-firmware",
                        "arch": "any",
                        "csize": "2483776",
                        "builddate": "1573556456",
                        "version": "20200204.b791e15-1",
                        "desc": "Firmware files for Linux",
                        "url": "https://kernel.org",
                        "license": "GPL2",
                        "packager": "Arch Dev <developer@archlinux.org>",
                        "conflicts": ["linux-firmware-git"],
                        "replaces": ["kernel26-firmware"],
                        "depends": [""],
                        "makedepends": ["git"],
                        "optdepends": [""]
                }]

        @pytest.fixture(scope="session")
        def localdb(generate_localdb, db_data):
                return generate_localdb(db_data)

        def test_handle(localdb):
                handle = Handle("/", localdb)
                localdb = handle.get_localdb()

Module
------

The package object for generate_syncdb/generate_localdb should be a dictionary with the following members:

.. code-block:: python

    {
        "name": "linux-firmware",
        "base": "linux-firmware",
        "arch": "any",
        "csize": "2483776",
        "builddate": "1573556456",
        "version": "20200204.b791e15-1",
        "desc": "Firmware files for Linux",
        "url": "https://kernel.org",
        "license": "GPL2",
        "packager": "Arch Dev <developer@archlinux.org>",
        "conflicts": ["linux-firmware-git"],
        "replaces": ["kernel26-firmware"],
        "depends": [""],
        "makedepends": ["git"],
        "optdepends": [""]
    }


.. py:function:: generate_syncdb(pkgs: list, dbname: string, dbloc: string)

    Generates a sync database in a provided location or when not provided pytest tmpdir

    :param list pkgs: a list of package objects
    :param str dbname: sync database name (default 'test.db')
    :param str dbloc: location where sync database will be created (optional)

    :returns: path to dbroot for when dbroot is not provided


.. py:function:: generate_localdb(pkgs: list, dbroot: string, alpm_db_version: string)

    Generates a sync database in a provided location or when not provided pytest tmpdir

    :param list pkgs: a list of package objects
    :param str dbroot: the path to the root (normally /var/lib/pacman)
    :param str alpm_db_version: the ALPM_DB_VERSION (default 9)

    :returns: path to dbroot for when dbroot is not provided


.. py:function:: generate_package(data: object, pkgname: string, pkgpath: string)

    Generates a package in provided location or when not provided pytest tmpdir

    :param object data:  dict containing the fields for PKGINFO
    :param str dbname: the package file name ($pkgname-$pkgver-$pkgrel.pkg.tar) 
    :param str dbloc: the path to save the pkg file

    :returns: path to the package
