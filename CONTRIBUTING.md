# Contributing to Röntgen

Thank you for your interest in contributing to the Röntgen icon set!

If you want to request a new icon, or found an error in the existing icons,
please [open an issue on GitHub](https://github.com/enzet/Roentgen/issues).

## Creating a Release

1. Change version in `VERSION` files:

```shell
echo "$VERSION_NUMBER" > VERSION
echo "$VERSION_NUMBER" > icons/VERSION
```

2. Change version in `pyproject.toml`.
3. Update `CHANGELOG.md`.

4. Commit and push.

```shell
git add VERSION icons/VERSION pyproject.toml CHANGELOG.md
git commit -m "Update version to $VERSION_NUMBER"
git push
```

5. Check if tests pass on GitHub.

6. If tests pass, add and push a tag:

```shell
git tag -a v$VERSION_NUMBER -m "Version $VERSION_NUMBER"
git push origin v$VERSION_NUMBER
```