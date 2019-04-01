from datetime import timedelta
from jetblack_auth.yaml.timedelta_handler import format_timedelta, parse_timedelta


def test_timedelta_roundtrip():
    for value in [
        timedelta(hours=15, minutes=12, seconds=38),
        timedelta(weeks=1, days=3, hours=15, minutes=12, seconds=38)
    ]:
        s = format_timedelta(value)
        roundtrip = parse_timedelta(s)
        assert value == roundtrip
