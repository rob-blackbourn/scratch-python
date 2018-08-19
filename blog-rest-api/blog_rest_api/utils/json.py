import json
import re
from datetime import date, datetime, timezone, timedelta, tzinfo
from bson import ObjectId


class JsonEncoderEx(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, bool):
            return str(o).lower()
        elif isinstance(o, ObjectId):
            return str(o)
        else:
            return super().default(o)


datetime_format = "%Y-%m-%dT%H:%M:%S"
datetime_format_regex = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')

datetime_tz_format = "%Y-%m-%dT%H:%M:%S%z"
datetime_tz_format_regex = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$')
datetime_tz_transform = re.compile(r'(?<=[+=][0-9]{2}):')

datetime_zulu_format_regex = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

datetime_ms_tz_format = "%Y-%m-%dT%H:%M:%S.%f%z"
datetime_ms_tz_format_regex = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$')


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and datetime_format_regex.match(v):
            dct[k] = datetime.strptime(v, datetime_format)
    return dct


date_format = "%Y-%m-%d"
date_format_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def date_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and date_format_regex.match(v):
            dct[k] = datetime.strptime(v, date_format).date()
    return dct


def date_or_datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str):
            if datetime_format_regex.match(v):
                dct[k] = datetime.strptime(v, datetime_format)
            elif datetime_tz_format_regex.match(v):
                v = re.sub(r'(?<=[+=][0-9]{2}):', '', v)
                d = datetime.strptime(v, datetime_tz_format)
                # if d.tzinfo == timezone.utc:
                #    d.replace(tzinfo = timedelta(0))
                dct[k] = d
            elif datetime_ms_tz_format_regex.match(v):
                v = re.sub(r'(?<=[+=][0-9]{2}):', '', v)
                v = re.sub(r'(\.\d{3})\d*', r'\1', v)
                d = datetime.strptime(v, datetime_ms_tz_format)
                if d.tzinfo == timezone.utc:
                    d.replace(tzinfo=timedelta(0))
                dct[k] = d
            elif datetime_zulu_format_regex.match(v):
                v = v[:-1] + "+0000"
                d = datetime.strptime(v, datetime_tz_format)
                if d.tzinfo == timezone.utc:
                    d.replace(tzinfo=timedelta(0))
                dct[k] = d
            elif date_format_regex.match(v):
                dct[k] = datetime.strptime(v, date_format)
    return dct


def date_or_datetime_parser_utc(dct):
    for k, v in dct.items():
        if isinstance(v, str):
            if datetime_format_regex.match(v):
                dct[k] = datetime.strptime(
                    v, datetime_format).astimezone(timezone.utc)
            elif datetime_tz_format_regex.match(v):
                v = re.sub(r'(?<=[+=][0-9]{2}):', '', v)
                dct[k] = datetime.strptime(
                    v, datetime_tz_format).astimezone(timezone.utc)
            elif datetime_ms_tz_format_regex.match(v):
                v = re.sub(r'(?<=[+=][0-9]{2}):', '', v)
                dct[k] = datetime.strptime(
                    v, datetime_ms_tz_format).astimezone(timezone.utc)
            elif date_format_regex.match(v):
                dct[k] = datetime.strptime(
                    v, date_format).replace(tzinfo=timezone.utc)
    return dct


if __name__ == "__main__":
    #a = {'a1': '2001-03-28', 'a2': '2005-08-12T12:15:59', 'a3':'2005-08-12T12:15:59+00:00', 'a4':'2017-10-05T09:37:32.187+02:00'}
    a = {'a4': '2017-10-06T07:43:19+00:00'}
    #b = datetime_parser(a.copy())
    #c = date_parser(a.copy())
    d = date_or_datetime_parser(a.copy())
