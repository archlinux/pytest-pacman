# pytest-pacman - pacman db pytest fixture

This is a pytest plugin which will generate a test pacman db. To be used in
pyalpm, archweb and arch-signoff for testing.

## Fixtures

* generate_syncdb
* generate_localdb
* generate_package

## Usage

Installing is as simple as e.g.

```
pip install pytest-pacman
```

## Pacman syncdb structure

Pacman syncdb databases are usually stored in '/var/lib/pacman/sync' as gzip'd
tar archives. The structure in the archive is as following:

```
$pkgname-$pkgver-$pkgrel/
$pkgname-$pkgver-$pkgrel/desc
$pkgname-$epoch:$pkgver-$pkgrel/
$pkgname-$epoch:$pkgver-$pkgrel/desc
```

The desc file is formatted as following:

```
%FILENAME%
$pkgname-$pkgver-$pkgrel-$arch.pkg.tar.$ext

%NAME%
$pkgname

%BASE%
$pkgbase

%VERSION%
$pkgver-$pkgrel

%DESC%
My awesome package

%CSIZE%
671256

%ISIZE%
3460513

%MD5SUM%
c9f6e74471bce4b07d0f54b75e65b27c

%SHA256SUM%
c5af2664d994671a61b5038c468e6b4dae5dde71785dd687216f67f28df956d3

%URL%
https://archlinux.org

%LICENSE%
BSD

%ARCH%
$arch

%BUILDDATE%
$epoch

%PACKAGER%
John Doe <package@archlinux.org>

%DEPENDS%
zlib
xz

%MAKEDEPENDS%
systemd
```
