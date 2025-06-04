# Contributing to Röntgen

Thank you for your interest in contributing to the Röntgen icon set! This
document provides guidelines and instructions for contributing to this project.

## Creating a Release

1. Change version in `VERSION` files.

```shell
echo "$VERSION_NUMBER" > VERSION
echo "$VERSION_NUMBER" > icons/VERSION
echo "$VERSION_NUMBER" > icons_by_name/VERSION
git add VERSION icons/VERSION icons_by_name/VERSION
```

2. Change version in `pyproject.toml`.

```shell
git add pyproject.toml
```

3. Commit and push.

```shell
git commit -m "Update version to $VERSION_NUMBER"
git push
```

4. Check if tests pass on GitHub.

```shell
git tag -a v$VERSION_NUMBER -m "Version $VERSION_NUMBER"
```

5. Add and push a tag.

```shell
git push origin v$VERSION_NUMBER
```