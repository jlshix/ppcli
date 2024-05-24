from __future__ import annotations
import tomllib
from argparse import Namespace
from pathlib import Path
from typing import Any


class PPCli:
    def __init__(self, command: str, conf: Conf, env: Path) -> None:
        self.command = command
        self.conf = conf
        self.env = env

    @classmethod
    def from_args(cls, args: Namespace) -> 'PPCli':
        return cls(
            command=args.command,
            conf=Conf.from_path(Path(args.config)),
            env=Path(args.env),
        )

    def list(self) -> list[str]:
        return self.conf.commands()


class Conf:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    @classmethod
    def from_path(cls, path: Path) -> 'Conf':
        if not path.exists():
            raise FileExistsError(f"{path} does not exist")
        with path.open() as f:
            data = tomllib.loads(f.read())
        scope = data.get("tool", {}).get("ppcli")
        if scope is None:
            raise ValueError(f"No tool.ppcli scope defined in {path}")
        if not isinstance(scope, dict):
            raise TypeError(f"tool.ppcli scope {scope} is not a dict")
        return cls(scope)

    def commands(self) -> list[str]:
        return sorted(self.data.keys())
