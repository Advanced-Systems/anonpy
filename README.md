<center>
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
    <a title="Downloads per Month">
        <img src="https://img.shields.io/pypi/dm/anonpy">
    </a>
    <a title="Supported Python Versions">
        <img src="https://img.shields.io/pypi/pyversions/anonpy">
    </a>
    <a href="https://github.com/Advanced-Systems/anonpy" title="Release Version">
        <img src="https://img.shields.io/pypi/v/anonpy?color=blue&label=Release">
    </a>
    <a href="https://github.com/Advanced-Systems/anonpy/blob/master/LICENSE" target="_blank" title="License">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg">
    </a>
  </div>
</center>

## About

The `anonpy` module provides the facilities for rapid application development in
the realm of anonymous file sharing. It implements an extensible provider-independent
class system for communicating with any REST API, and also comes with an intuitive
CLI or lightweight GUI for direct client usage.

## Library

You can use `AnonPy` to interface with a wide variety of REST services by
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

You can also use the [Wiki](https://github.com/Advanced-Systems/anonpy/wiki)
page for more in-depth examples or to read more about intrinsic development details.

## Command Line Interface

Read the help manual:

```powershell
anonpy --help
```

## Graphical User Interface

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

See also the list of [contributors](https://github.com/Advanced-Systems/anonpy/contributors)
who participated in the development of this project.

## Further Reading

This Project is licensed under the [MIT](https://github.com/Advanced-Systems/anonpy/blob/master/LICENSE) license.
Check out the [Contributing Guidelines](https://github.com/Advanced-Systems/anonpy/blob/master/CONTRIBUTING.md)
to learn more about how you can help this project grow.
Navigate to the [Discussions](https://github.com/Advanced-Systems/anonpy/discussions)
panel to ask questions or make feature requests.
