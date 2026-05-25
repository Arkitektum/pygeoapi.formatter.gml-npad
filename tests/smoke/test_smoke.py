"""End-to-end smoke: postgres → postgresql_ext → formatter → GML string.

What this exercises that the unit tests don't:

- Real SQLAlchemy reflection against a postgres table with dot-bearing,
  diacritic-preserving column names
- ``property_shape: dotted`` mode in postgresql_ext (v0.3.0+), passing the
  raw column dict through without nesting or leaf-stripping
- The formatter's ``write()`` against real psycopg-typed values (psycopg
  date / Decimal / etc. flowing through ``_format_value``)

Geometry is intentionally *not* exercised here — the smoke schema has the
binary geom column but no ``_geometry_gml`` text column yet. That arrives
with postgresql_ext PR2 (``gml_passthrough``) + corresponding MV column
additions. Formatter ``validate=False`` until then.
"""

import pytest

pytestmark = pytest.mark.smoke

# Imports at module scope so a missing postgresql_ext fails collection loudly
# rather than silently skipping.
from postgresql_ext import PostgreSQLExtendedProvider  # noqa: E402

from pygeoapi_formatter_gml_npad.kommuneplan_20190401 import (  # noqa: E402
    KommuneplanFormatter,
)
from pygeoapi_formatter_gml_npad.reguleringsplan_20190401 import (  # noqa: E402
    ReguleringsplanFormatter,
)


def _query_features(provider_def: dict) -> dict:
    """Instantiate the provider and return its query() FeatureCollection."""
    provider = PostgreSQLExtendedProvider(provider_def)
    return provider.query()


# ---------------------------------------------------------------------------
# Provider-side contract: property_shape: dotted produces dot-bearing keys
# ---------------------------------------------------------------------------


def test_rp_provider_emits_dotted_property_keys(rp_provider_def):
    fc = _query_features(rp_provider_def)

    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 1

    props = fc["features"][0]["properties"]
    # Dot-bearing keys present verbatim — proves postgresql_ext's
    # property_shape: dotted is passing through the reflected column names
    # rather than nesting or leaf-stripping.
    assert "identifikasjon.lokalId" in props
    assert props["identifikasjon.lokalId"] == "rp-smoke-001"
    assert "arealplanId.kommunenummer" in props
    assert props["arealplanId.kommunenummer"] == "301"
    assert "kopidata.kopidato" in props


def test_kp_provider_emits_dotted_property_keys(kp_provider_def):
    fc = _query_features(kp_provider_def)

    props = fc["features"][0]["properties"]
    assert "identifikasjon.lokalId" in props
    assert props["identifikasjon.lokalId"] == "kp-smoke-001"
    assert "arealplanId.kommunenummer" in props


# ---------------------------------------------------------------------------
# Formatter-side: serialize the provider's output to schema-shaped GML
# ---------------------------------------------------------------------------


def _assert_envelope(gml: str, schema_namespace: str, feature_count: int) -> None:
    assert gml.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<wfs:FeatureCollection " in gml
    assert f'numberReturned="{feature_count}"' in gml
    assert schema_namespace in gml  # in xsi:schemaLocation
    assert "</wfs:FeatureCollection>" in gml


def test_rp_full_chain_serializes_to_gml(rp_provider_def):
    fc = _query_features(rp_provider_def)

    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "validate": False})
    gml = fmt.write({}, fc)

    _assert_envelope(gml, ReguleringsplanFormatter.SCHEMA_NAMESPACE, feature_count=1)

    # Nested group: <app:identifikasjon><app:Identifikasjon><app:lokalId>
    assert "<app:identifikasjon>" in gml
    assert "<app:Identifikasjon>" in gml
    assert "<app:lokalId>rp-smoke-001</app:lokalId>" in gml

    # Nested group: arealplanId with the zero-pad rule on kommunenummer
    assert "<app:arealplanId>" in gml
    assert "<app:NasjonalArealplanId>" in gml
    # kommunenummer fixture is '301'; zero_pad_columns says width 4 → '0301'
    assert "<app:kommunenummer>0301</app:kommunenummer>" in gml

    # Simple property
    assert "<app:plantype>35</app:plantype>" in gml

    # gml:id derived from id_prefix + monotonic counter, not from objid
    assert 'gml:id="rpomrade.1"' in gml


def test_kp_full_chain_serializes_to_gml(kp_provider_def):
    fc = _query_features(kp_provider_def)

    fmt = KommuneplanFormatter({"feature_type": "KpOmråde", "validate": False})
    gml = fmt.write({}, fc)

    _assert_envelope(gml, KommuneplanFormatter.SCHEMA_NAMESPACE, feature_count=1)

    assert "<app:identifikasjon>" in gml
    assert "<app:lokalId>kp-smoke-001</app:lokalId>" in gml
    assert "<app:kommunenummer>0301</app:kommunenummer>" in gml
    assert "<app:plantype>20</app:plantype>" in gml
    assert 'gml:id="kpomrade.1"' in gml


# ---------------------------------------------------------------------------
# Negative signal: pre-PR2, geometry should NOT appear in the output
# ---------------------------------------------------------------------------


def test_geometry_absent_until_gml_passthrough_ships(rp_provider_def):
    """Until postgresql_ext PR2 adds ``gml_passthrough`` (which injects
    ``_geometry_gml`` into properties), the formatter receives no GML-text
    for the geometry and skips the element entirely. This test locks that
    pre-PR2 behavior so we notice the transition when PR2 lands."""
    fc = _query_features(rp_provider_def)

    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "validate": False})
    gml = fmt.write({}, fc)

    # No <app:område> wrapper because _geometry_gml is missing from the row
    assert "<app:område>" not in gml
    assert "<gml:Polygon" not in gml
