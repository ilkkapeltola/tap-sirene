"""REST client handling, including SIRENEStream base class."""

import requests
import base64
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator

import json

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class SIRENEStream(RESTStream):
    """SIRENE stream class."""

    # TODO: Set the API's base URL here:
    url_base = "https://api.insee.fr/entreprises/sirene/V3"
    first_run = True

    # OR use a dynamic url_base:
    # @property
    # def url_base(self) -> str:
    #     """Return the API URL root, configurable via tap settings."""
    #     return self.config["api_url"]

    #records_jsonpath = self.records_jsonpath  # Or override `parse_response`.
    #next_page_token_jsonpath = "$.next_page"  # Or override `get_next_page_token`.

    # extra_retry_statuses: List[int] = [429, 400]

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""

        key = "%s:%s" % (self.config.get("consumer_key"), self.config.get("consumer_secret"))
        key_bytes = key.encode('ascii')
        key_b64 = base64.b64encode(key_bytes).decode('utf-8')
        endpoint = "https://api.insee.fr/token"
        headers = { 'Authorization' : 'Basic %s' % (key_b64)}
        data = "grant_type=client_credentials".encode('ascii')

        response = requests.post(endpoint, data=data, headers=headers)
        jdata = response.json()
        

        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=jdata["access_token"]
            #token="0521bf46-bc5a-3bc7-93e3-9b29fcd37459"
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        # TODO: If pagination is required, return a token which can be used to get the
        #       next page. If this is the final page, return "None" to end the
        #       pagination loop.

        #total = next(iter(extract_jsonpath("$.header.total", response.json())),None)
        #debut = next(iter(extract_jsonpath("$.header.debut", response.json())),None)
        #nombre = next(iter(extract_jsonpath("$.header.nombre", response.json())),None)

        total = next(iter(extract_jsonpath("$.header.total", response.json())),None)
        debut = next(iter(extract_jsonpath("$.header.debut", response.json())),None)
        nombre = next(iter(extract_jsonpath("$.header.nombre", response.json())),None)

        if total > debut + nombre:
            last_timestamp = next(iter(extract_jsonpath(self.last_timestamp_path, response.json())),None)
            return (last_timestamp)
        else:
            return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}

        params["nombre"] = "1000"
        start_date = self.config.get("start_date")

        bookmark_date = self.get_starting_timestamp(context)
        
        if bookmark_date:
            start_date = bookmark_date.strftime("%Y-%m-%dT%H:%M:%S")

        # overrides after first run
        if next_page_token:
            start_date = next_page_token

        params["tri"] = self.replication_key

        params["q"] = "%s:[%s TO %s]" % (self.replication_key, start_date, self.config.get("end_date") )

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())
