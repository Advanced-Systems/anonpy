#!/usr/bin/env python3

import difflib
import json
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Tuple

from colorama import Fore, Style, deinit, just_fix_windows_console
from requests.exceptions import HTTPError
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

from .anonpy import AnonPy, Endpoint
from .cli import build_parser
from .internals import ConfigHandler, LogLevel, RequestHandler, __credits__, __package__, __version__, get_resource_path, join_url, read_file, str2bool
from .security import MD5, Checksum

#region helpers

def print_diff(a: str, b: str, console: Console) -> None:
        diff = difflib.ndiff(
            f"{a}\n".splitlines(keepends=True),
            f"{b}\n".splitlines(keepends=True)
        )

        console.print("".join(diff), end="")

def copy_to_clipboard(text: str) -> None:
    subprocess.run("clip", input=text, check=True, encoding="utf-8")

#endregion

#region commands

def preview(anon: AnonPy, args: Namespace, config: ConfigHandler, console: Console) -> None:
    verbose = args.verbose or config.get_option("client", "verbose")

    for resource in args.resource:
        preview = anon.preview(resource)
        console.print(JSON(json.dumps(preview)) if verbose else ",".join(preview.values()))

def upload(anon: AnonPy, args: Namespace, config: ConfigHandler, console: Console) -> None:
    verbose = args.verbose or config.get_option("client", "verbose")

    for file in args.file:
        upload = anon.upload(file, progressbar=verbose)
        url = upload.get("url", False) or join_url(anon.api.geturl(), anon.endpoint.download.format(upload["id"]))
        anon.logger.info("Uploaded %s to %s" % (file, url))

        if args.clip: copy_to_clipboard(url)

        if not verbose: continue
        computed_hash = Checksum.compute(path=file, algorithm=MD5)
        checksum = Checksum.hash2string(computed_hash)
        console.print(f"URL={url}")
        console.print(f"MD5={checksum}")

def download(anon: AnonPy, args: Namespace, config: ConfigHandler, console: Console) -> None:
    download_directory = Path(getattr(args, "path", config.get_option("client", "download_directory")))
    verbose = args.verbose or config.get_option("client", "verbose")
    force = args.force or config.get_option("client", "force")

    for resource in (args.resource or read_file(args.batch_file)):
        preview = anon.preview(resource)
        file = preview.get("name")

        if file is None:
            console.print("Aborting download: unable to determine file name property from preview response", style="bold red")
            anon.logger.error("Download Error: resource %s responded with %s" % (args.resource, str(preview)), stacklevel=2)
            continue

        if not force and download_directory.joinpath(file).exists():
            console.print(f"[bold yellow]WARNING:[/] The file {str(file)} already exists in {str(download_directory)}.")
            prompt = console.input("Proceed with download? [dim][Y/n][/] ")
            if not str2bool(prompt): continue

        anon.download(resource, download_directory, progressbar=verbose)

        if getattr(args, "checksum", None) is None: continue
        computed_hash = Checksum.compute(path=file, algorithm=MD5)
        computed_checksum = Checksum.hash2string(computed_hash)

        if verbose: console.print(f"MD5={computed_checksum}")

        expected_checksum = args.checksum
        corrupt = computed_checksum != expected_checksum

        if not corrupt: continue
        print_diff(computed_checksum, expected_checksum, console)

#endregion

def _start(module_folder: Path, cfg_file: str) -> Tuple[ArgumentParser, Console]:
    # Enable Windows' built-in ANSI support
    just_fix_windows_console()
    console = Console(color_system="256")

    # Configure parser
    description = f"{Fore.WHITE}{Style.DIM}Command line interface for anonymous file sharing.{Style.RESET_ALL}"
    epilog = f"{Fore.WHITE}{Style.DIM}Authors: {','.join(__credits__)}{Style.RESET_ALL}"
    parser = build_parser(__package__, __version__, description, epilog)

    # Initialize default settings
    cfg_path = module_folder / cfg_file

    if not cfg_path.exists():
        with ConfigHandler(cfg_path) as config_handler:
            config_handler.add_section("client", settings={
                "download_directory": Path("~/downloads").expanduser(),
                "token": None,
                "user_agent": None,
                "proxies": None,
                "enable_logging": False,
                "log_level": LogLevel.INFO.value,
                "verbose": True,
                "force": False,
            })

            config_handler.add_section("server", settings={
                "api": "https://pixeldrain.com/api/",
                "upload": "/file",
                "download": "/file{}",
                "preview": "/file/{}/info"
            })

    return (parser, console)

def main() -> None:
    module_folder = get_resource_path(__package__)
    cfg_file = "anonpy.ini"
    log_file = "anonpy.log"

    parser, console = _start(module_folder, cfg_file)
    args = parser.parse_args()

    config = ConfigHandler(getattr(args, "config", module_folder / cfg_file))
    config.read()

    kwargs = {
        "api": config.get_option("server", "api"),
        "endpoint": Endpoint(config.get_option("server", "upload"), config.get_option("server", "download"), config.get_option("server", "preview")),
        "token": getattr(args, "token", config.get_option("client", "token")),
        "proxies": getattr(args, "proxies", config.get_option("client", "proxies")),
        "user_agent": getattr(args, "user_agent", config.get_option("client", "user_agent")) or RequestHandler.build_user_agent(__package__, __version__),
        "enable_logging": args.logging or config.get_option("client", "enable_logging"),
    }

    provider = AnonPy(**kwargs)
    provider.logger \
        .set_base_path(module_folder) \
        .with_level(LogLevel(config.get_option("client", "log_level"))) \
        .add_handler(log_file)

    if args.gui:
        raise NotImplementedError("This feature is not implemented yet, see also: https://github.com/Advanced-Systems/anonpy/discussions/11")

    try:
        match args.command:
            case "preview":
                preview(provider, args, config, console)
            case "upload":
                upload(provider, args, config, console)
            case "download":
                download(provider, args, config, console)
            case _:
                raise NotImplementedError()

    except KeyboardInterrupt:
        pass
    except NotImplementedError:
        parser.print_help()
    except HTTPError as http_error:
        provider.logger.error("Request failed with HTTP status code %d (%s)" % (http_error.response.status_code, http_error.response.text), stacklevel=2)
        console.print(http_error.response.text, style="bold red")
    except Exception as exception:
        provider.logger.critical(exception, stacklevel=2)
        console.print_exception(show_locals=True)
    except:
        console.print(Panel(
            "\n".join([
                f"An unhandled exception was thrown. The log file may give you more insight into what went wrong: [bold yellow]{module_folder}[/].",
                f"Alternatively, file a bug report on GitHub at [bold blue]https://github.com/advanced-systems/anonpy[/]."
            ])
        ))
    finally:
        deinit()
        provider.logger.shutdown()

if __name__ == "__main__":
    main()
