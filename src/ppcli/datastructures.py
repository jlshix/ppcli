from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, NamedTuple


class Target(NamedTuple):
    script: str
    variables: dict[str, str]

    @classmethod
    def parse(cls, data: dict[str, str | dict[str, str]]) -> Target:
        try:
            script = data["script"]
        except KeyError:
            raise ValueError("`script` field is required")
        if not isinstance(script, str):
            raise TypeError(
                f"`script` field type must be a string, but got {type(script)}"
            )
        variables = data.get("variables") or {}
        if not isinstance(variables, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in variables.items()
        ):
            raise TypeError("`variables` field should be a dict of str and str")
        return cls(script, variables)


class Targets:
    def __init__(self, targets: dict[str, Target]) -> None:
        self.targets = targets

    def __contains__(self, item: str) -> bool:
        return item in self.targets

    def __getitem__(self, key: str) -> Target:
        return self.targets[key]

    def names(self) -> list[str]:
        return sorted(self.targets.keys())

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Targets:
        exceptions = []
        targets = {}
        for name, values in data.items():
            try:
                targets[name] = Target.parse(values)
            except Exception as e:
                exceptions.append(e)
        if exceptions:
            raise ExceptionGroup(
                "parse ppcli targets failed",
                exceptions,
            )
        return cls(targets=targets)


class Conf:
    def __init__(self, data: dict[str, Any]) -> None:
        raw_targets = {k: v for k, v in data.items() if not k.startswith("_")}
        self.variables: dict[str, str] = data.get("_variables", {})
        self.targets = Targets.parse(raw_targets)

    def __contains__(self, key: str) -> bool:
        return key in self.targets

    @classmethod
    def from_path(cls, path: Path) -> "Conf":
        if not path.exists():
            raise FileExistsError(f"{path} does not exist")
        with path.open() as f:
            try:
                data = tomllib.loads(f.read())
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"{path} is not a valid TOML file") from e

        scope = data.get("tool", {}).get("ppcli")
        if scope is None:
            raise ValueError(f"No tool.ppcli scope defined in {path}")
        if not isinstance(scope, dict):
            raise TypeError(f"tool.ppcli scope {scope} is not a dict")
        return cls(scope)

    def target_names(self) -> list[str]:
        return sorted(self.targets.names())

    def target_variables(self, target_name: str) -> dict[str, str]:
        try:
            target_variables = self.targets[target_name].variables
        except KeyError:
            raise ValueError(f"Invalid target name {target_name}")
        return {
            **self.variables,
            **target_variables,
        }
