"""Stream type classes for tap-sirene."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sirene.client import SIRENEStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class SiretStream(SIRENEStream):
    """Define custom stream."""
    name = "siret"
    path = "/siret"
    records_jsonpath = "$.etablissements[*]"
    primary_keys = ["siret"]
    replication_key = "dateDernierTraitementEtablissement"
    last_timestamp_path = "$.etablissements[-1].dateDernierTraitementEtablissement"
    is_timestamp_replication_key = True
    is_sorted = True
    replication_method = "INCREMENTAL"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / "siret.json"

class SirenStream(SIRENEStream):
    """Define custom stream."""
    name = "siren"
    path = "/siren"
    primary_keys = ["siren"]
    is_sorted = True
    records_jsonpath = "$.unitesLegales[*]"
    last_timestamp_path = "$.unitesLegales[-1].dateDernierTraitementUniteLegale"
    replication_key = "dateDernierTraitementUniteLegale"
    is_timestamp_replication_key = True
    replication_method = "INCREMENTAL"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema_filepath = SCHEMAS_DIR / "siren.json"