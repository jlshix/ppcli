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
    print(conf.job_names())


def cmd_run(args: Namespace) -> None:
    CmdRun.from_args(args).run()


class CmdRun:
    def __init__(
        self,
        conf: Conf,
        job: list[str],
        dot_envs: list[str],
        job_envs: list[str],
        use_os_env: bool,
    ) -> None:
        self.conf = conf
        self.job = job
        self.dot_envs = dot_envs
        self.job_envs = job_envs
        self.use_os_env = use_os_env

    @classmethod
    def from_args(cls, args: Namespace) -> "CmdRun":
        return cls(
            conf=Conf.from_path(Path(args.config)),
            job=args.job,
            dot_envs=args.dot_envs,
            job_envs=args.job_envs,
            use_os_env=args.use_os_env,
        )

    def load_envs(self) -> dict[str, str]:
        rv = dict(os.environ) if self.use_os_env else {}
        for dotenv in self.dot_envs:
            values = dotenv_values(dotenv_path=dotenv)
            rv |= values
        job_envs = "\n".join(self.job_envs)
        values = dotenv_values(stream=StringIO(job_envs))
        rv |= values
        return rv

    def run(self) -> None:
        if job_len := len(self.job) != 1:
            raise ValueError(f"Invalid job length: {job_len}, accepts name only")
        job = self.job[0]
        if job not in self.conf:
            raise ValueError(
                f"Invalid job: {job}, accepts one of {self.conf.job_names()}"
            )
        script = self.conf.jobs[job].script
        envs = self.load_envs()
        envs.update(self.conf.job_variables(job_name=job))
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

    list_parser = sub_parsers.add_parser("list", help="list jobs")
    list_parser.set_defaults(func=cmd_list)

    run_parser = sub_parsers.add_parser("run", help="run job")
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
        dest="job_envs",
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

    run_parser.add_argument("job", nargs=REMAINDER, help="job to run")
    run_parser.set_defaults(func=cmd_run)
    args = parser.parse_args()
    args.func(args)
