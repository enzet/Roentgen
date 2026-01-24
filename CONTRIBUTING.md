# Contributing to Röntgen

Thank you for your interest in contributing to the Röntgen icon set!

## What Contributions Are Welcome

Röntgen is a personal design project, and I want to keep it that way. Icon
design is inherently subjective, and this project reflects my personal
preferences, so I cannot add icons drawn by someone else to the set.

However, the following contributions are **highly welcome**:
  - Request icon coverage for your preferred OpenStreetMap tags.
  - Suggest new icons or design changes (please open an issue for discussion).
  - Improvements and bugfixes in the Python code (pull requests are welcome).

## Setup Development Environment

  1. Install development dependencies: `pip install -e .[dev]`.
  2. Install Rust implementation of iconscript: `cargo install iconscript@0.3`.
  3. Enable pre-commit hooks: `git config --local core.hooksPath .githooks`.

## Creating a Release

1. Change version in `VERSION` files:

```shell
echo "$VERSION_NUMBER" > VERSION
echo "$VERSION_NUMBER" > icons/VERSION
```

2. Change version in `pyproject.toml`, and `package.json`.
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

7. Create ZIP file with icons:

```shell
cp -r icons/ release/roentgen-$VERSION_NUMBER
cd release
zip -r roentgen-$VERSION_NUMBER.zip roentgen-$VERSION_NUMBER/
cd ..
```

8. Create new GitHub Release:

```shell
gh release create v$VERSION_NUMBER \
    --title "Version $VERSION_NUMBER" \
    release/roentgen-$VERSION_NUMBER.zip
```

9. Build and publish Python package:

```shell
rm -r dist/
source .venv/bin/activate
python -m build
python -m twine upload dist/roentgen_icons-$VERSION_NUMBER*
deactivate
cd ..
```

10. Publish npm package:

```shell
npm publish --access public
```
