import datetime
import json
import time
import random
import urllib.parse

from ._common import log
from . import _exception

from typing import Iterable, Optional, Any

#: Default list of user agents
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/601.1.10 (KHTML, like Gecko) Version/8.0.5 Safari/601.1.10",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; ; NCT50_AAP285C84A1328) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
]


def get_limits(limit: Optional[int], max_limit: int) -> Iterable[int]:
    """Helper that generates limits based on a max limit."""
    if limit is None:
        # Generate infinite items
        while True:
            yield max_limit

    if limit < 0:
        raise ValueError("Limit cannot be negative")

    # Generate n items
    yield from [max_limit] * (limit // max_limit)

    remainder = limit % max_limit
    if remainder:
        yield remainder


def json_minimal(data: Any) -> str:
    """Get JSON data in minimal form."""
    return json.dumps(data, separators=(",", ":"))


def strip_json_cruft(text: str) -> str:
    """Removes `for(;;);` (and other cruft) that preceeds JSON responses."""
    try:
        return text[text.index("{") :]
    except ValueError as e:
        raise _exception.ParseError("No JSON object found", data=text) from e


def parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError as e:
        raise _exception.ParseError("Error while parsing JSON", data=text) from e


def generate_offline_threading_id():
    ret = datetime_to_millis(datetime.datetime.utcnow())
    value = int(random.random() * 4294967295)
    string = ("0000000000000000000000" + format(value, "b"))[-22:]
    msgs = format(ret, "b") + string
    return str(int(msgs, 2))


def get_jsmods_require(j, index):
    if j.get("jsmods") and j["jsmods"].get("require"):
        try:
            return j["jsmods"]["require"][0][index][0]
        except (KeyError, IndexError) as e:
            log.warning(
                "Error when getting jsmods_require: "
                "{}. Facebook might have changed protocol".format(j)
            )
    return None


def mimetype_to_key(mimetype: str) -> str:
    if not mimetype:
        return "file_id"
    if mimetype == "image/gif":
        return "gif_id"
    x = mimetype.split("/")
    if x[0] in ["video", "image", "audio"]:
        return "%s_id" % x[0]
    return "file_id"


def get_url_parameter(url: str, param: str) -> Optional[str]:
    params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if not params.get(param):
        return None
    return params[param][0]


def seconds_to_datetime(timestamp_in_seconds: float) -> datetime.datetime:
    """Convert an UTC timestamp to a timezone-aware datetime object."""
    # `.utcfromtimestamp` will return a "naive" datetime object, which is why we use the
    # following:
    return datetime.datetime.fromtimestamp(
        timestamp_in_seconds, tz=datetime.timezone.utc
    )


def millis_to_datetime(timestamp_in_milliseconds: int) -> datetime.datetime:
    """Convert an UTC timestamp, in milliseconds, to a timezone-aware datetime."""
    return seconds_to_datetime(timestamp_in_milliseconds / 1000)


def datetime_to_seconds(dt: datetime.datetime) -> int:
    """Convert a datetime to an UTC timestamp.

    Naive datetime objects are presumed to represent time in the system timezone.

    The returned seconds will be rounded to the nearest whole number.
    """
    # We could've implemented some fancy "convert naive timezones to UTC" logic, but
    # it's not really worth the effort.
    return round(dt.timestamp())


def datetime_to_millis(dt: datetime.datetime) -> int:
    """Convert a datetime to an UTC timestamp, in milliseconds.

    Naive datetime objects are presumed to represent time in the system timezone.

    The returned milliseconds will be rounded to the nearest whole number.
    """
    return round(dt.timestamp() * 1000)


def seconds_to_timedelta(seconds: float) -> datetime.timedelta:
    """Convert seconds to a timedelta."""
    return datetime.timedelta(seconds=seconds)


def millis_to_timedelta(milliseconds: int) -> datetime.timedelta:
    """Convert a duration (in milliseconds) to a timedelta object."""
    return datetime.timedelta(milliseconds=milliseconds)


def timedelta_to_seconds(td: datetime.timedelta) -> int:
    """Convert a timedelta to seconds.

    The returned seconds will be rounded to the nearest whole number.
    """
    return round(td.total_seconds())
