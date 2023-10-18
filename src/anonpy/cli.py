#!/usr/bin/env python3

from argparse import ArgumentParser, HelpFormatter, SUPPRESS
from pathlib import Path

def build_parser(package_name: str, version: str, description: str, epilog: str) -> ArgumentParser:
    formatter = lambda prog: HelpFormatter(prog,max_help_position=52)
    parser = ArgumentParser(prog=package_name, description=description, epilog=epilog, formatter_class=formatter)
    parser._positionals.title = "Commands"
    parser._optionals.title = "Arguments"

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {version}")
    parser.add_argument("--verbose", default=True, action="store_true", help="increase output verbosity")
    parser.add_argument("--logging", default=False, action="store_true", help="log request history")
    parser.add_argument("--token", type=str, default=SUPPRESS, help="set API token")
    parser.add_argument("--user-agent", type=str, default=SUPPRESS, help="set custom user-agent")
    parser.add_argument("--proxies", type=str, default=SUPPRESS, help="set HTTP/HTTPS proxies")
    parser.add_argument("--config", type=Path, default=SUPPRESS, help="path to config file")
    parser.add_argument("--gui", default=False, action="store_true", help="launch the GUI frontend")
    parser.add_argument("--reset-config", default=False, action="store_true", help="reset default config file")

    subparser = parser.add_subparsers(dest="command")
    upload_parser = subparser.add_parser("upload", help="upload a file")
    upload_parser.add_argument("-f", "--file", nargs="+", type=Path, help="one or more files to upload.", required=True)
    upload_parser.add_argument("-c", "--clip", default=False, action="store_true", help="copy download URL to clipboard")
    upload_parser.add_argument("--algorithm", type=str, default=SUPPRESS, help="checksum algorithm")

    preview_parser = subparser.add_parser("preview", help="read meta data from a remote file")
    preview_parser.add_argument("-r", "--resource", nargs="+", type=str, help="one or more resources to preview", required=True)

    download_parser = subparser.add_parser("download", help="download a file")
    download_urls_group = download_parser.add_mutually_exclusive_group(required=True)
    download_urls_group.add_argument("-r", "--resource", nargs="*", type=str, help="one or more resources to download")
    download_urls_group.add_argument("--batch-file", type=Path, nargs="?", help="file containing resources to download")
    download_parser.add_argument("-p", "--path", type=Path, default=SUPPRESS, help="download directory (CWD by default)")
    download_parser.add_argument("-f", "--force", default=False, action="store_true", help="overwrite duplicates, if any")
    download_parser.add_argument("--checksum", type=str, default=SUPPRESS, help="expected MD5 checksum value for integrity test")
    download_parser.add_argument("--hash", type=str, default=SUPPRESS, help="checksum algorithm")

    return parser
