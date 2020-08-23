# pytest-pacman - pacman db pytest fixture

This is a pytest plugin which will generate a test pacman db.

## Fixtures

The fixtures this plugin should provide:

* generate_localdb(packages)

* syncdb (/var/lib/pacman/sync/$repo.db)
* localdb (/var/lib/local/pacman/local/$pkgname-$epoch-$pkgver-$pkgrel/)
* files db (/var/lib/pacman/sync/$repo.files)
* syncdb with different compressions (zst,gz) as file

## Usage

Installing is as simple as e.g.

```
pip install pytest-pacman
```
