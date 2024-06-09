from pathlib import Path

import pytest

from ppcli.datastructures import Conf

conf_folder = Path(__file__).parent / "files"


def test_conf_not_exist():
    with pytest.raises(FileNotFoundError) as exc:
        Conf.from_path(conf_folder / "not_exist.toml")
    assert "does not exist" in str(exc.value)


def test_conf_not_toml():
    with pytest.raises(ValueError) as exc:
        Conf.from_path(conf_folder / "pyproject.json")
    assert "not a valid TOML file" in str(exc.value)


def test_conf_no_ppcli_scope():
    with pytest.raises(ValueError) as exc:
        Conf.from_path(conf_folder / "pyproject_no_ppcli.toml")
    assert "No tool.ppcli scope defined" in str(exc.value)


def test_conf_ppcli_not_dict():
    with pytest.raises(TypeError) as exc:
        Conf.from_path(conf_folder / "pyproject_ppcli_not_dict.toml")
    assert "tool.ppcli scope is not a dict" in str(exc.value)


def test_conf_no_job():
    conf = Conf.from_path(conf_folder / "pyproject_test_no_job.toml")
    assert bool(conf.jobs) is False
    assert conf.job_names() == []
    assert conf.variables == {"GLOBAL": "global"}


@pytest.fixture()
def conf() -> Conf:
    return Conf.from_path(conf_folder / "pyproject_test.toml")


def test_conf_valid(conf):
    assert "test" in conf
    assert conf.job_names() == [
        'build', 'check', 'format', 'install', 'mypy', 'show_env', 'test', 'uninstall'
    ]


def test_conf_job_variables(conf):
    with pytest.raises(ValueError) as exc:
        conf.job_variables(job_name="not_existed_job")
    assert "Invalid job name" in str(exc.value)
    expected = {'GLOBAL': 'GLB', 'LOCAL': 'LOCAL'}
    assert conf.job_variables(job_name="show_env") == expected
