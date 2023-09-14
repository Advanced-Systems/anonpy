from setuptools import find_packages, setup
from typing import Optional, List

#region helper functions

def read_file(path: str, split: Optional[bool]=False) -> str | List[str]:
    with open(path, mode='r', encoding="utf-8") as file_handler:
        return file_handler.readlines() if split else file_handler.read()

#endregion

print("processing setup function")

setup(
    name="anonpy",
    version="0.1.0",
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
        "Bug Reports": "https://github.com/advanced-systems/anonpy/issues"
    },
    python_requires=">=3.11",
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
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="anonfile rest api anonymous file sharing"
)

print("setup is complete")
