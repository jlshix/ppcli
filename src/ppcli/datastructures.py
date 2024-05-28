from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, NamedTuple


class Job(NamedTuple):
    script: str
    variables: dict[str, str]

    @classmethod
    def parse(cls, data: dict[str, str | dict[str, str]]) -> Job:
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


class Jobs:
    def __init__(self, jobs: dict[str, Job]) -> None:
        self.jobs = jobs

    def __contains__(self, item: str) -> bool:
        return item in self.jobs

    def __getitem__(self, key: str) -> Job:
        return self.jobs[key]

    def names(self) -> list[str]:
        return sorted(self.jobs.keys())

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Jobs:
        exceptions = []
        jobs = {}
        for name, values in data.items():
            try:
                jobs[name] = Job.parse(values)
            except Exception as e:
                exceptions.append(e)
        if exceptions:
            raise ExceptionGroup(
                "parse ppcli jobs failed",
                exceptions,
            )
        return cls(jobs=jobs)


class Conf:
    def __init__(self, data: dict[str, Any]) -> None:
        raw_jobs = {k: v for k, v in data.items() if not k.startswith("_")}
        self.variables: dict[str, str] = data.get("_variables", {})
        self.jobs = Jobs.parse(raw_jobs)

    def __contains__(self, key: str) -> bool:
        return key in self.jobs

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

    def job_names(self) -> list[str]:
        return sorted(self.jobs.names())

    def job_variables(self, job_name: str) -> dict[str, str]:
        try:
            job_variables = self.jobs[job_name].variables
        except KeyError:
            raise ValueError(f"Invalid job name {job_name}")
        return {
            **self.variables,
            **job_variables,
        }
