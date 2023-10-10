#!/usr/bin/env python3

import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from colorama import Fore, Style, deinit, just_fix_windows_console
from requests.exceptions import HTTPError

from .anonpy import AnonPy
from .cli import build_parser
from .internals import ConfigHandler, LogLevel, RequestHandler, __credits__, __package__, __version__, get_resource_path, read_file, str2bool
from .providers import PixelDrain
from .security import MD5, Checksum

#region commands

def preview(anon: AnonPy, args: Namespace, config: ConfigHandler) -> None:
    verbose = args.verbose or config.get_option("client", "verbose")

    for resource in args.resource:
        preview = anon.preview(resource)
        print(json.dumps(preview, indent=4) if verbose else ",".join(preview.values()))

def upload(anon: AnonPy, args: Namespace, config: ConfigHandler) -> None:
    verbose = args.verbose or config.get_option("client", "verbose")

    for file in args.file:
        anon.upload(file, progressbar=verbose)

        if not verbose: continue
        md5 = Checksum.compute(path=file, algorithm=MD5)
        print(f"MD5={Checksum.hash2string(md5)}")

def download(anon: AnonPy, args: Namespace, config: ConfigHandler) -> None:
    download_directory = Path(getattr(args, "path", config.get_option("client", "download_directory")))
    verbose = args.verbose or config.get_option("client", "verbose")
    check = args.check or config.get_option("client", "check")

    for resource in (args.resource or read_file(args.batch_file)):
        preview = anon.preview(resource)
        file = preview.get("name")

        if file is None:
            print("Aborting download: unable to read file name property from preview response", file=sys.stderr)
            anon.logger.error("Download Error: resource %s responded with %s" % (args.resource, str(preview)))
            continue

        if check and download_directory.joinpath(file).exists():
            print(f"WARNING: The file {str(file)!r} already exists in {str(download_directory)!r}.")
            prompt = input("Proceed with download? [Y/n] ")
            if not str2bool(prompt): continue

        anon.download(resource, download_directory, progressbar=verbose)

        if not verbose: continue
        md5 = Checksum.compute(path=file, algorithm=MD5)
        print(f"MD5={Checksum.hash2string(md5)}")

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
                "check": True,
            })

    return parser

def main() -> None:
    module_folder = get_resource_path(__package__)
    cfg_file = "anonpy.ini"
    log_file = "anonpy.log"

    parser = _start(module_folder, cfg_file)
    args = parser.parse_args()

    config = ConfigHandler(getattr(args, "config", module_folder / cfg_file))
    config.read()

    kwargs = {
        "token": getattr(args, "token", config.get_option("client", "token")),
        "proxies": getattr(args, "proxies", config.get_option("client", "proxies")),
        "user_agent": getattr(args, "user_agent", config.get_option("client", "user_agent")) or RequestHandler.build_user_agent(__package__, __version__),
        "enable_logging": args.logging or config.get_option("client", "enable_logging"),
    }

    # NOTE: Uses the PixelDrain provider by default for now
    provider = PixelDrain(**kwargs)
    provider.logger \
        .set_base_path(module_folder) \
        .with_level(LogLevel(config.get_option("client", "log_level"))) \
        .add_handler(log_file)

    try:
        match args.command:
            case "preview":
                preview(provider, args, config)
            case "upload":
                upload(provider, args, config)
            case "download":
                download(provider, args, config)
            case _:
                raise NotImplementedError()

    except KeyboardInterrupt:
        pass
    except NotImplementedError:
        parser.print_help()
    except HTTPError as http_error:
        provider.logger.error("Request failed with HTTP status code %d (%s)" % (http_error.response.status_code, http_error.response.text), stacklevel=1)
        print(http_error.response.text, file=sys.stderr)
    except Exception as exception:
        provider.logger.critical(exception, stacklevel=1)
        print(exception.with_traceback(), file=sys.stderr)
    except:
        print("\n".join([
            "An unhandled exception was thrown. The log file may give you more",
            f"insight into what went wrong: {module_folder!r}.\nAlternatively, file",
            "a bug report on GitHub at https://github.com/advanced-systems/anonpy."
        ]), file=sys.stderr)
    finally:
        deinit()
        provider.logger.shutdown()

if __name__ == "__main__":
    main()
