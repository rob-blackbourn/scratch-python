import pytest
from datetime import time

from ruamel.yaml import StringIO
from jetblack_yaml import make_yaml


@pytest.mark.unit
def test_valid_time():
    yaml = make_yaml()

    test_case = "!time 00:00:00.000000"
    res = yaml.load(test_case)

    assert isinstance(res, time)

    assert res.hour == 0
    assert res.minute == 0
    assert res.second == 0
    assert res.microsecond == 0

    with StringIO() as sout:
        yaml.dump(res, sout)
        yaml_output = sout.getvalue()

        # ruamel.yaml adds new lines, so can only test startswith
        # as per isoformat convention, omit the microseconds when it is zero
        assert yaml_output.startswith("!time 00:00:00")

    test_case = "!time 23:59:59.999999"
    res = yaml.load(test_case)
    assert isinstance(res, time)

    assert res.hour == 23
    assert res.minute == 59
    assert res.second == 59
    assert res.microsecond == 999999

    with StringIO() as sout:
        yaml.dump(res, sout)
        yaml_output = sout.getvalue()

        # ruamel.yaml adds new lines, so can only test startswith
        assert yaml_output.startswith(test_case)


@pytest.mark.unit
def test_invalid_time():
    yaml = make_yaml()

    with pytest.raises(ValueError) as e_info:
        yaml.load("""!time 24:00:00.000000""")

    assert "hour" in str(e_info.value)
