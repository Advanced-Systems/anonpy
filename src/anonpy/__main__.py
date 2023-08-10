#!/usr/bin/env python3

import sys
from argparse import Namespace

from colorama import Fore, Style, just_fix_windows_console, deinit
from requests import HTTPError

from .anonpy import AnonPy, ServerResponse
from .internals import RequestHandler
from .cli import build_parser
from .internals import ConfigHandler
from .metadata import __package__, __version__, __credits__

#region commands

def preview(anon: AnonPy, args: Namespace) -> None:
    raise NotImplementedError()

def upload(anon: AnonPy, args: Namespace) -> None:
    raise NotImplementedError()

def download(anon: AnonPy, args: Namespace) -> None:
    raise NotImplementedError()

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
        "user_agent": RequestHandler._build_user_agent(__package__, __version__)
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
