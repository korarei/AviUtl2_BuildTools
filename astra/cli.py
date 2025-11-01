import argparse
from pathlib import Path
from typing import Any

from astra.core import build, install, package, template


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="astra")
    sub: Any = parser.add_subparsers(dest="command", required=True)

    def _build(args: argparse.Namespace) -> None:
        build.build(args.source / args.config)

    def _install(args: argparse.Namespace) -> None:
        install.install(args.source / args.config, args.destination)

    def _package(args: argparse.Namespace) -> None:
        package.package(args.source / args.config)

    def _init(args: argparse.Namespace) -> None:
        template.init(args.output, args.force)

    def add_common_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-s", "--source",
            nargs='?',
            type=Path,
            default=Path.cwd(),
            help="Source directory (default: current directory)"
        )
        parser.add_argument(
            "-c", "--config",
            nargs='?',
            type=str,
            default="astra.config.json",
            help="Configuration file name (default: astra.config.json)"
        )

    p_build: argparse.ArgumentParser = sub.add_parser(
        "build", help="Build scripts for AviUtl2")
    add_common_args(p_build)
    p_build.set_defaults(func=_build)

    p_install: argparse.ArgumentParser = sub.add_parser(
        "install", help="Copy build artifacts to the target installation directory")
    add_common_args(p_install)
    p_install.add_argument(
        "-d", "--destination",
        nargs='?',
        type=Path,
        default=None,
        help="Destination directory for installation (default: as defined in config)"
    )
    p_install.set_defaults(func=_install)

    p_package: argparse.ArgumentParser = sub.add_parser(
        "package", help="Create a distributable package from the project")
    add_common_args(p_package)
    p_package.set_defaults(func=_package)

    p_init: argparse.ArgumentParser = sub.add_parser(
        "init", help="Generate a template JSON configuration file for a new project")
    p_init.add_argument(
        "-o", "--output",
        nargs='?',
        type=Path,
        default=Path.cwd(),
        help="Destination directory for the generated configuration file (default: current directory)"
    )
    p_init.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite if exists"
    )
    p_init.set_defaults(func=_init)

    args: argparse.Namespace = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
