import pytest
from datetime import timedelta
from jetblack_yaml import make_yaml

from ruamel.yaml import StringIO


@pytest.mark.unit
def test_valid_timedelta():
    yaml = make_yaml()

    res = yaml.load("""!timedelta 1w""")
    assert isinstance(res, timedelta)
    assert res.days == 7
    assert res.seconds == 0

    res = yaml.load("""!timedelta 1m""")
    assert isinstance(res, timedelta)
    assert res.days == 0
    assert res.seconds == 60

    res = yaml.load("""!timedelta 61s""")
    assert isinstance(res, timedelta)
    assert res.days == 0
    assert res.seconds == 61

    res = yaml.load("""!timedelta 1w2d5h1m30s""")
    assert isinstance(res, timedelta)
    assert res.days == 9
    assert res.seconds == 18090


@pytest.mark.unit
def test_timedelta_roundtrip():
    test_cases = [
        "!timedelta 1w2d5h1m30s",
        "!timedelta 2d5h1m30s",
        "!timedelta 0s",
    ]

    yaml = make_yaml()

    for test_case in test_cases:
        res = yaml.load(test_case)

        with StringIO() as sout:
            yaml.dump(res, sout)
            yaml_output = sout.getvalue()

            # ruamel.yaml adds new lines, so can only test startswith
            assert yaml_output.startswith(test_case)
