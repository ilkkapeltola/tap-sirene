"""SIRENE tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers
# TODO: Import your custom stream types here:
from tap_sirene.streams import (
    SIRENEStream,
    SiretStream,
    SirenStream
)
# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    SiretStream,
    SirenStream
]


class TapSIRENE(Tap):
    """SIRENE tap class."""
    name = "tap-sirene"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "consumer_key",
            th.StringType,
            required=True,
            description="The consumer key"
        ),
        th.Property(
            "consumer_secret",
            th.StringType,
            required=True,
            description="The consumer secret"
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        ),
        th.Property(
            "end_date",
            th.DateTimeType,
            description="The last record date to sync"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
