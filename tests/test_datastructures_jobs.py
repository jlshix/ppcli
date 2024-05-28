import pytest

from ppcli.datastructures import Job


@pytest.mark.parametrize(
    ("data", "job"),
    [
        (
                {"script": "echo hello world"},
                Job(script="echo hello world", variables={}),
        ),
        (
                {"script": "echo hello $name", "variables": {"name": "world"}},
                Job(script="echo hello $name", variables={"name": "world"})
        )
    ]
)
def test_job_parse(data: dict, job: Job):
    assert Job.parse(data) == job


def test_job_parse_key_error():
    with pytest.raises(KeyError) as exc:
        Job.parse({})
    assert exc.value.args[0] == "`script` field is required"


def test_job_parse_data_type_error():
    with pytest.raises(TypeError) as exc:
        Job.parse('{"script": "echo hello"}')  # noqa
    assert exc.value.args[0] == "data must be a dict, but got <class 'str'>"


def test_job_parse_script_type_error():
    with pytest.raises(TypeError) as exc:
        Job.parse({"script": ["echo", "hello"]})  # noqa
    assert exc.value.args[0] == "`script` field type must be a string, but got <class 'list'>"


def test_job_parse_variables_type_error():
    with pytest.raises(TypeError) as exc:
        Job.parse({
            "script": "echo hello $name",
            "variables": ["name=world"],
        })
    assert exc.value.args[0] == "`variables` field should be a dict[str, str]"
