<div align="center">
  <a href="https://github.com/advanced-systems/anonpy" title="Project Logo">
    <img height="150" style="margin-top:15px" src="https://raw.githubusercontent.com/advanced-systems/anonpy/master/logo.svg">
  </a>
  <h1>AnonPy</h1>
  <div>
    <a href="https://github.com/Advanced-Systems/anonpy/actions/workflows/python-build-test.yml" target="_blank" title="Python Build Test">
        <img src="https://github.com/Advanced-Systems/anonpy/actions/workflows/python-build-test.yml/badge.svg">
    </a>
    <a href="https://github.com/Advanced-Systems/anonpy/actions/workflows/codeql.yml" target="_blank" title="Code QL">
        <img src="https://github.com/Advanced-Systems/anonpy/actions/workflows/codeql.yml/badge.svg">
    </a>
    <a href="https://codecov.io/gh/Advanced-Systems/anonpy" target="_blank" title="Code Coverage">
        <img src="https://codecov.io/gh/Advanced-Systems/anonpy/graph/badge.svg?token=64NLA38DP4">
    </a>
    <a href="https://pypistats.org/packages/anonpy" target="_blank" title="Downloads per Month">
        <img src="https://img.shields.io/pypi/dm/anonpy?label=Downloads">
    </a>
    <a href="https://www.python.org/downloads/release/python-3120/" target="_blank" title="Supported Python Version">
        <img src="https://img.shields.io/pypi/pyversions/anonpy?label=Python">
    </a>
    <a href="https://github.com/Advanced-Systems/anonpy" target="_blank" title="Release Version">
        <img src="https://img.shields.io/pypi/v/anonpy?color=blue&label=Release">
    </a>
    <a href="https://github.com/Advanced-Systems/anonpy/blob/master/LICENSE" target="_blank" title="License">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg">
    </a>
  </div>
</div>

## About

The `anonpy` module makes it easier to communicate with REST APIs for anonymously
uploading and downloading files. It implements an extensible provider-independent
class system and also comes with an intuitive CLI or lightweight GUI for interactive
usage.

> ⚠ This project is still a work in progress. Keep an eye on the
> [Roadmap](https://github.com/Advanced-Systems/anonpy/milestone/1),
> which documents the progress path toward the first major release.

Documentation for this project is located on the GitHub
[Wiki](https://github.com/Advanced-Systems/anonpy/wiki)
page.

## Installation

> ⚠ It is currently not possible to install this library with `pip` yet, but
> you may install the release candidate for testing purposes.

`anonpy` is available on PyPI:

```powershell
pip install anonpy
```

Release candidates (preview versions) of this library can be installed with:

```powershell
pip install -i https://test.pypi.org/simple/ anonpy
```

To ensure a clean and isolated environment for running `anonpy`'s CLI, it is
recommended to install it with the [`pipx`](https://pypa.github.io/pipx/) command.

```powershell
pipx install anonpy
```

## Library

`anonpy` can be used to interface with a wide variety of REST services by
building a contract with the `Endpoint` class.

```python
from anonpy import AnonPy, Endpoint

api = "https://pixeldrain.com/api/"
endpoint = Endpoint(upload="/file", download="file/{}", preview="/file/{}/info")

anon = AnonPy(api, endpoint)

# retrieve resource meta data without committing to a download
preview = anon.preview("LNcXZ9UM")
print(f"{preview=}")

# download a resource to the current working directory
download = anon.download("LNcXZ9UM", progressbar=True)
print(f"{download=}")

# upload a file
upload = anon.upload("homework.docx", progressbar=True)
print(f"{upload=}")
```

## Command Line Interface

Read the help manual:

```powershell
anonpy --help
```

## Graphical User Interface

> ⚠ This feature is currently not implemented yet, but is expected to be released
> in version 1.2.0

Launch a graphical user interface for uploading and downloading files:

```powershell
anonpy --gui
```

## Acknowledgements

Historically speaking, this module can be considered a continuation of the
[`anonfile-api`](https://github.com/nstrydom2/anonfile-api/) project, although
any resemblance of compatibility may only be temporary. On 16 August 2023, the
anonymous file sharing website <https://anonfiles.com> shut down due to overwhelming
abuse by the community, which was the driving factor for creating a backend-agnostic
library that can stand the test of time. That's why to this day, `anonpy` still
uses the anonfiles logo as a small nod to its past.

Special thanks to [@aaronlyy](https://github.com/aaronlyy) for passing on the
PyPI name [`anonpy`](https://pypi.org/project/anonpy/) to [@StefanGreve](https://github.com/aaronlyy).

See also the list of
[contributors](https://github.com/Advanced-Systems/anonpy/contributors)
who participated in the development of this project.

## Further Reading

This Project is licensed under the
[MIT](https://github.com/Advanced-Systems/anonpy/blob/master/LICENSE)
license.
Check out the
[Contributing Guidelines](https://github.com/Advanced-Systems/anonpy/blob/master/CONTRIBUTING.md)
to learn more about how you can help this project grow.
Navigate to the
[Discussions](https://github.com/Advanced-Systems/anonpy/discussions)
panel to ask questions or make feature requests.
