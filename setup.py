#!/usr/bin/env python3

from typing import List, Optional

from setuptools import find_packages, setup

#region helper functions

def read_file(path: str, split: Optional[bool]=False) -> str | List[str]:
    with open(path, mode='r', encoding="utf-8") as file_handler:
        return file_handler.readlines() if split else file_handler.read()

#endregion

print("processing setup function")

setup(
    name="anonpy",
    version="1.0.0",
    license="MIT",
    author="Stefan Greve",
    author_email="greve.stefan@outlook.jp",
    maintainer="Stefan Greve",
    maintainer_email="greve.stefan@outlook.jp",
    description="A slick and modern Python package for anonymous file sharing",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/advanced-systems/anonpy",
    project_urls={
        "Source Code": "https://github.com/advanced-systems/anonpy",
        "Bug Reports": "https://github.com/advanced-systems/anonpy/issues",
        "Documentation": "https://github.com/advanced-systems/anonpy/wiki",
        "Changelog": "https://github.com/advanced-systems/anonpy/blob/master/README.md"
    },
    python_requires=">=3.12",
    install_requires=read_file("requirements/release.txt", split=True),
    extra_requires={
        "dev": read_file("requirements/development.txt", split=True)[1:]
    },
    package_dir={
        "": "src",
    },
    packages=find_packages(where="src"),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "anonpy=anonpy.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="advanced systems anonpy rest api anonymous file sharing"
)

print("setup is complete")
