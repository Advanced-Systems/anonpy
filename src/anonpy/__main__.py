#!/usr/bin/env python3

import json
import sys
from argparse import Namespace

from colorama import Fore, Style, deinit, just_fix_windows_console
from requests import HTTPError

from .anonpy import AnonPy, ServerResponse
from .cli import build_parser
from .internals import ConfigHandler, RequestHandler, read_file, str2bool
from .metadata import __credits__, __package__, __version__

#region commands

def preview(anon: AnonPy, args: Namespace) -> None:
    for url in args.url:
        preview = anon.preview(url)
        data = {
            "Status": "online" if preview.status else "offline",
            "ID": preview.id,
            "URL": preview.url,
            "DDL": preview.ddl.geturl(),
            "File Path": preview.file_path.name,
            "Size": preview.size_readable,
        }

        print(json.dumps(data, indent=4) if args.verbose else ",".join(data.values()))

def upload(anon: AnonPy, args: Namespace) -> None:
    for file in args.file:
        upload = anon.upload(file, progressbar=args.verbose)
        print(upload.url)

def download(anon: AnonPy, args: Namespace) -> None:
    for url in (args.url or read_file(args.batch_file)):
        if args.check and anon.preview(url, args.path).file_path.exists():
            print(f"Warning: A file with the same name already exists in {str(args.path)!r}.")
            prompt = input("Proceed with download? [Y/n] ")
            if not str2bool(prompt): continue

        download = anon.download(url, args.path, progressbar=args.verbose)
        print(f"File: {download.file_path}")

#endregion

def cli() -> None:
    # enable Windows' built-in ANSI support
    just_fix_windows_console()

    description = f"{Fore.WHITE}{Style.DIM}Command line interface for anonymous file sharing.{Style.RESET_ALL}"
    epilog = f"{Fore.WHITE}{Style.DIM}Authors: {','.join(__credits__)}{Style.RESET_ALL}"

    parser = build_parser(__package__, __version__, description, epilog)
    args = parser.parse_args()

    kwargs = {
        "base": "https://api.anonfiles.com/",
        "user_agent": RequestHandler.build_user_agent(__package__, __version__),
        "enable_logging": args.logging,
    }

    try:
        anon = AnonPy(**kwargs)

        match args.command:
            case "preview":
                preview(anon, args)
            case "upload":
                upload(anon, args)
            case "download":
                download(anon, args)
            case _:
                raise NotImplementedError()

    except KeyboardInterrupt:
        pass
    except NotImplementedError:
        parser.print_help()
    except HTTPError as http_error:
        server_response = ServerResponse(http_error.response.json(), None, None)
        print(server_response.status_code, file=sys.stderr)
    except Exception as exception:
        print(exception, file=sys.stderr)
    except:
        print("\n".join([
            Fore.RED,
            "FATAL ERROR",
            Style.RESET_ALL,
            "An unhandled exception was thrown. The log file may give you more",
            "insight into what went wrong. Alternatively, file a bug report on",
            "GitHub at https://github.com/advanced-systems/anonpy."
        ]), file=sys.stderr)
    finally:
        deinit()

if __name__ == "__main__":
    cli()
