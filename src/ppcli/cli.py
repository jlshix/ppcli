from __future__ import annotations

import os
import subprocess
from argparse import ArgumentParser, REMAINDER, Namespace
from io import StringIO
from pathlib import Path

from dotenv import dotenv_values

from . import __version__
from .datastructures import Conf


def cmd_list(args: Namespace) -> None:
    conf = Conf.from_path(Path(args.config))
    print(conf.target_names())


def cmd_run(args: Namespace) -> None:
    CmdRun.from_args(args).run()


class CmdRun:
    def __init__(
        self,
        conf: Conf,
        target: list[str],
        dot_envs: list[str],
        target_envs: list[str],
        use_os_env: bool,
    ) -> None:
        self.conf = conf
        self.target = target
        self.dot_envs = dot_envs
        self.target_envs = target_envs
        self.use_os_env = use_os_env

    @classmethod
    def from_args(cls, args: Namespace) -> "CmdRun":
        return cls(
            conf=Conf.from_path(Path(args.config)),
            target=args.target,
            dot_envs=args.dot_envs,
            target_envs=args.target_envs,
            use_os_env=args.use_os_env,
        )

    def load_envs(self) -> dict[str, str]:
        rv = dict(os.environ) if self.use_os_env else {}
        for dotenv in self.dot_envs:
            values = dotenv_values(dotenv_path=dotenv)
            rv |= values
        target_envs = "\n".join(self.target_envs)
        values = dotenv_values(stream=StringIO(target_envs))
        rv |= values
        return rv

    def run(self) -> None:
        if target_len := len(self.target) != 1:
            raise ValueError(f"Invalid target length: {target_len}, accepts name only")
        target = self.target[0]
        if target not in self.conf:
            raise ValueError(
                f"Invalid target: {target}, accepts one of {self.conf.target_names()}"
            )
        script = self.conf.targets[target].script
        envs = self.load_envs()
        envs.update(self.conf.target_variables(target_name=target))
        subprocess.run(script, shell=True, env=envs)


def main() -> None:
    parser = ArgumentParser(
        description="run scripts defined in pyproject.toml",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-c",
        "--config",
        help="pyproject.toml path, defaults to ./pyproject.toml",
        default="./pyproject.toml",
    )

    sub_parsers = parser.add_subparsers(required=True)

    list_parser = sub_parsers.add_parser("list", help="list targets")
    list_parser.set_defaults(func=cmd_list)

    run_parser = sub_parsers.add_parser("run", help="run target")
    run_parser.add_argument(
        "-d",
        "--dotenv",
        dest="dot_envs",
        nargs="*",
        default=[],
        help=".dotenv path, such as .dotenv .env.secret",
    )
    run_parser.add_argument(
        "-e",
        "--env",
        dest="target_envs",
        nargs="*",
        default=[],
        help="environment variables, formatted the same as dotenv contents",
    )

    run_parser.add_argument(
        "--use-os-env",
        dest="use_os_env",
        default=True,
        help="use os.environ variables if set to True",
    )

    run_parser.add_argument("target", nargs=REMAINDER, help="target to run")
    run_parser.set_defaults(func=cmd_run)
    args = parser.parse_args()
    args.func(args)
