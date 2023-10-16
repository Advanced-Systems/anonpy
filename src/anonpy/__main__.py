#!/usr/bin/env python3

import difflib
import json
import subprocess
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Dict, Optional

from colorama import Fore, Style, deinit, just_fix_windows_console
from requests.exceptions import HTTPError
from rich.json import JSON
from rich.panel import Panel

from .anonpy import AnonPy, Endpoint
from .cli import build_parser
from .internals import ConfigHandler, LogLevel, RequestHandler, __credits__, __package__, __version__, console, get_resource_path, join_url, read_file, str2bool
from .security import MD5, Checksum

#region helpers

type EvalConfig = Dict[str, Dict[str, Optional[Any]]]

def print_diff(a: str, b: str) -> None:
        diff = difflib.ndiff(
            f"{a}\n".splitlines(keepends=True),
            f"{b}\n".splitlines(keepends=True)
        )

        console.print("".join(diff), end="")

def copy_to_clipboard(text: str) -> None:
    subprocess.run("clip", input=text, check=True, encoding="utf-8")

def init_config(cfg_path: Path) -> None:
    """
    Create a new configuration file by force, potentially overwriting existing data.
    """
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
            "download": "/file/{}",
            "preview": "/file/{}/info"
        })

def eval_config(args: Namespace, config: ConfigHandler) -> EvalConfig:
    """
    Return a dictionary of config values, giving preference to command line arguments.
    Some values have a fallback in case neither `args` nor `config` provide a value,
    if `None` is not acceptable.
    """
    settings = {
        "client": {
            "download_directory": Path(getattr(args, "path", config.get_option("client", "download_directory", default=Path.cwd()))),
            "token": getattr(args, "token", config.get_option("client", "token")),
            "user_agent": getattr(args, "user_agent", config.get_option("client", "user_agent", default=RequestHandler.build_user_agent(__package__, __version__))),
            "proxies": getattr(args, "proxies", config.get_option("client", "proxies")),
            "enable_logging": getattr(args, "logging", config.get_option("client", "enable_logging")),
            "log_level": config.get_option("client", "log_level"),
            "verbose": getattr(args, "verbose", config.get_option("client", "verbose")),
            "force": getattr(args, "force", config.get_option("client", "force")),
        },
        "server": {
            "api": config.get_option("server", "api"),
            "upload": config.get_option("server", "upload"),
            "download": config.get_option("server", "download"),
            "preview": config.get_option("server", "preview"),
        }
    }

    settings["object"] = {
        "endpoint": Endpoint(settings["server"]["upload"], settings["server"]["download"], settings["server"]["preview"]),
    }

    return settings

#endregion

#region commands

def preview(anon: AnonPy, args: Namespace, settings: EvalConfig) -> None:
    client = settings["client"]

    for resource in args.resource:
        with console.status("fetching data...") as _:
            preview = anon.preview(resource)
            console.print(JSON(json.dumps(preview)) if client["verbose"] else ",".join(preview.values()))

def upload(anon: AnonPy, args: Namespace, settings: EvalConfig) -> None:
    client = settings["client"]

    for file in args.file:
        upload = anon.upload(file, enable_progressbar=client["verbose"])
        url = upload["url"]
        anon.logger.info("Uploaded %s to %s" % (file, url))
        console.print(f"URL={url}")

        if args.clip: copy_to_clipboard(url)

        if not client["verbose"]: continue
        computed_hash = Checksum.compute(path=file, algorithm=MD5)
        checksum = Checksum.hash2string(computed_hash)
        console.print(f"MD5=[bold blue]{checksum}[/]")

def download(anon: AnonPy, args: Namespace, settings: EvalConfig) -> None:
    client = settings["client"]

    for resource in (args.resource or read_file(args.batch_file)):
        with console.status("fetching data...") as _:
            preview = anon.preview(resource)
            name = preview["name"]
            size = int(preview["size"])

        full_path = client["download_directory"] / name

        if not client["force"] and full_path.exists():
            console.print(f"[bold yellow]WARNING:[/] The file [bold blue]{str(full_path)}[/] already exists")
            prompt = console.input("Proceed with download? [dim][Y/n][/] ")
            if not str2bool(prompt): continue

        anon.download(resource, client["download_directory"], enable_progressbar=client["verbose"], size=size, name=name)
        console.print(f"PATH=[bold blue]{str(full_path)}[/]")

        if getattr(args, "checksum", None) is None: continue
        computed_hash = Checksum.compute(path=name, algorithm=MD5)
        computed_checksum = Checksum.hash2string(computed_hash)

        if client["verbose"]: console.print(f"MD5={computed_checksum}")

        expected_checksum = args.checksum
        corrupt = computed_checksum.lower() != expected_checksum.lower()

        if corrupt: print_diff(computed_checksum, expected_checksum, console)

#endregion

def _start(module_folder: Path, cfg_file: str) -> ArgumentParser:
    # Enable Windows' built-in ANSI support
    just_fix_windows_console()

    # Configure parser
    description = f"{Fore.WHITE}{Style.DIM}Command line interface for anonymous file sharing.{Style.RESET_ALL}"
    epilog = f"{Fore.WHITE}{Style.DIM}Authors: {','.join(__credits__)}{Style.RESET_ALL}"
    parser = build_parser(__package__, __version__, description, epilog)

    # Initialize default settings
    cfg_path = module_folder / cfg_file
    if not cfg_path.exists(): init_config(cfg_path)

    return parser

def main() -> None:
    module_folder = get_resource_path(__package__)
    cfg_file = "anonpy.ini"
    log_file = "anonpy.log"

    parser = _start(module_folder, cfg_file)
    args = parser.parse_args()

    config = ConfigHandler(getattr(args, "config", module_folder / cfg_file))
    config.read()

    settings = eval_config(args, config)
    kwargs = {
        k: v for k, v in settings["client"].items()
        if k in ["api", "token", "proxies", "user_agent", "enable_logging"]
    } | settings["object"] | {"api": settings["server"]["api"]}

    provider = AnonPy(**kwargs)
    provider.logger \
        .set_base_path(module_folder) \
        .with_level(LogLevel(settings["client"]["log_level"])) \
        .add_handler(log_file)

    if args.gui:
        console.print("[bold red]ERROR:[/] This feature is not implemented yet, see also: https://github.com/Advanced-Systems/anonpy/discussions/11")
        return

    if args.reset_config:
        config.path.unlink(missing_ok=True)
        init_config(config.path)
        return

    try:
        match args.command:
            case "preview":
                preview(provider, args, settings)
            case "upload":
                upload(provider, args, settings)
            case "download":
                download(provider, args, settings)
            case _:
                # argparse prints the help manual and exits if there are any
                # errors on parsing, so there's no need to handle this case
                # here as it will accomplish nothing
                pass

    except KeyboardInterrupt:
        pass
    except HTTPError as http_error:
        provider.logger.error("ERROR: Request failed with HTTP status code %d (%s)" % (http_error.response.status_code, http_error.response.text), stacklevel=2)
        console.print(http_error.response.text, style="bold red")
    except Exception as exception:
        provider.logger.critical(exception, stacklevel=2)
        console.print_exception(show_locals=True)
    except:
        console.print(Panel(
            "\n".join([
                "[bold red]FATAL ERROR[/]",
                f"An unhandled exception was thrown. The log file may give you more insight into what went wrong: [bold yellow]{module_folder}[/].",
                f"Alternatively, file a bug report on GitHub at [bold blue]https://github.com/advanced-systems/anonpy[/]."
            ])
        ))
    finally:
        deinit()
        provider.logger.shutdown()

if __name__ == "__main__":
    main()
