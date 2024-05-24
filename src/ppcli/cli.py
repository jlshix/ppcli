from argparse import ArgumentParser

from ppcli import __version__
from ppcli.datastructures import PPCli


def main():
    parser = ArgumentParser(
        description="un shell command defined in pyproject.toml",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__
    )
    parser.add_argument(
        "-c", "--config",
        help="pyproject.toml path, defaults to ./pyproject.toml",
        default="./pyproject.toml",
    )
    parser.add_argument(
        "-d", "--dotenv", "-e", "--env",
        dest="env",
        help=".dotenv path, defaults to ./.dotenv",
        default="./.dotenv",
    )

    sub_parsers = parser.add_subparsers(dest="command", required=True)
    sub_parsers.add_parser("list", help="list commands")
    sub_parsers.add_parser("run", help="run command")
    args = parser.parse_args()
    cli = PPCli.from_args(args)
    match args.command:
        case "list":
            print(cli.list())
        case "run":
            print("not yet implemented")


if __name__ == '__main__':
    main()
