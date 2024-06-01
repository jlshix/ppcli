import pytest

from ppcli.datastructures import Job, Jobs


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


@pytest.mark.parametrize(
    ("data", "jobs"),
    [
        (
            {
                "hello": {
                    "script": "echo hello $name",
                    "variables": {"name": "world"},
                },
                "build": {
                    "script": "python3 -m build --wheel",
                },
            },
            Jobs(jobs={
                "hello": Job(
                    script="echo hello $name",
                    variables={"name": "world"}
                ),
                "build": Job(
                    script="python3 -m build --wheel",
                    variables={},
                )
            })
        )
    ]

)
def test_jos_parse_success(data, jobs):
    parsed_jobs = jobs.parse(data)
    assert parsed_jobs == jobs
    assert jobs.names() == ["build", "hello"]
    assert jobs["hello"].script == "echo hello $name"


def test_jos_parse_failed():
    with pytest.raises(ExceptionGroup) as exc:
        Jobs.parse({
            "build": {"script": ["python", "-m", "build"]},
            "hello": {
                "script": "echo hello $name",
                "variables": ["name=world"],
            },
        })
    assert str(exc.value) == 'parse ppcli jobs failed (2 sub-exceptions)'
