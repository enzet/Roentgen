"""
Röntgen project dynamic metadata.
"""
from pathlib import Path

from setuptools import setup
from roentgen import (
    __author__,
    __description__,
    __email__,
    __url__,
    __version__,
)

with Path("README.md").open(encoding="utf-8") as input_file:
    long_description: str = input_file.read()

setup(
    name="roentgen",
    version=__version__,
    packages=["roentgen"],
    url=__url__,
    project_urls={
        "Bug Tracker": f"{__url__}/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    author=__author__,
    author_email=__email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": ["roentgen=roentgen.__main__:main"],
    },
    python_requires=">=3.9",
    install_requires=[
        "colour~=0.1.5",
        "svgwrite~=1.4.3",
        "numpy~=1.25.2",
        "svgpathtools~=1.6.1",
    ]
)
