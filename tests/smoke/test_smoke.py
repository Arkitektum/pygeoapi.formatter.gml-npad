"""End-to-end smoke: postgres → postgresql_ext → formatter → GML string.

What this exercises that the unit tests don't:

- Real SQLAlchemy reflection against a postgres table with dot-bearing,
  diacritic-preserving column names
- ``property_shape: dotted`` mode in postgresql_ext (v0.3.0+), passing the
  raw column dict through without nesting or leaf-stripping
- ``gml_passthrough: true`` (v0.4.0+): the provider injects a server-side
  ``ST_AsGML`` rendering of the geometry as a synthetic ``_geometry_gml``
  property, which the formatter passes through into the feature element
- The formatter's ``write()`` against real psycopg-typed values (psycopg
  date / Decimal / etc. flowing through ``_format_value``)
- ``validate=True``: the serialized first feature is XSD-validated against
  the real SOSI schemas from skjema.geonorge.no (network needed on cold
  cache; cached under /tmp/xsd-cache or $PYGEOAPI_GML_NPAD_XSD_CACHE_DIR)
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
from tests.helpers import gml_ids  # noqa: E402


def _query_features(provider_def: dict) -> dict:
    """Instantiate the provider and return its query() FeatureCollection."""
    provider = PostgreSQLExtendedProvider(provider_def)
    return provider.query()


# ---------------------------------------------------------------------------
# Provider-side contract: property_shape: dotted produces dot-bearing keys,
# gml_passthrough produces _geometry_gml
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


def test_provider_injects_geometry_gml(rp_provider_def):
    """gml_passthrough: true must surface a pre-rendered GML 3.2 string as
    a top-level synthetic property, alongside (not nested under) the
    dotted user keys."""
    fc = _query_features(rp_provider_def)

    props = fc["features"][0]["properties"]
    assert "_geometry_gml" in props
    geom_gml = props["_geometry_gml"]
    assert geom_gml.startswith("<gml:Polygon")
    # Long CRS URN — ST_AsGML options bit 1
    assert 'srsName="urn:ogc:def:crs:EPSG::25833"' in geom_gml


# ---------------------------------------------------------------------------
# Formatter-side: serialize the provider's output to schema-shaped GML
# ---------------------------------------------------------------------------


def _assert_envelope(gml: str, schema_namespace: str, feature_count: int) -> None:
    assert gml.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<gml:FeatureCollection " in gml
    assert gml.count("<gml:featureMember>") == feature_count
    assert schema_namespace in gml  # in xsi:schemaLocation
    assert "</gml:FeatureCollection>" in gml
    # gml:id is required on gml:FeatureCollection, and every id in the
    # document follows the '_' + UUID v4 scheme.
    assert len(gml_ids(gml)) == gml.count("gml:id=")


def test_rp_full_chain_serializes_to_gml(rp_provider_def):
    fc = _query_features(rp_provider_def)

    # validate=True is the real gate: the first feature is validated
    # against the SOSI XSD (downloaded from skjema.geonorge.no on first
    # use, cached on disk afterward — needs network on cold cache).
    # Fixtures carry every XSD-REQUIRED element so this passes.
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "validate": True})
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

    # Geometry: provider-rendered ST_AsGML passed through into the
    # XSD-ordered <app:område> wrapper, with a gml:id injected by the writer
    # and the ST_AsGML srsName URN rewritten to its OGC URI form
    assert "<app:område><gml:Polygon" in gml
    assert 'srsName="http://www.opengis.net/def/crs/EPSG/0/25833"' in gml
    assert "urn:ogc:def" not in gml
    assert "</gml:Polygon></app:område>" in gml

    _, feature_id, geometry_id = gml_ids(gml)
    assert geometry_id == f"{feature_id}-0"


def test_kp_full_chain_serializes_to_gml(kp_provider_def):
    fc = _query_features(kp_provider_def)

    fmt = KommuneplanFormatter({"feature_type": "KpOmråde", "validate": True})
    gml = fmt.write({}, fc)

    _assert_envelope(gml, KommuneplanFormatter.SCHEMA_NAMESPACE, feature_count=1)

    assert "<app:identifikasjon>" in gml
    assert "<app:lokalId>kp-smoke-001</app:lokalId>" in gml
    assert "<app:kommunenummer>0301</app:kommunenummer>" in gml
    assert "<app:plantype>20</app:plantype>" in gml

    # KP: DB geom column is `geometri`, GML element is `område`
    assert "<app:område><gml:Polygon" in gml

    _, feature_id, geometry_id = gml_ids(gml)
    assert geometry_id == f"{feature_id}-0"


def test_rp_grense_full_chain_validates(rpformalgrense_provider_def):
    """Grense (boundary) chain: representative of all 29 grense types,
    which share one XSD shape (Fellesegenskaper_LinjerOgPunkt base + a
    single `grense` curve element, no arealplanId). validate=True is the
    point — element-order mistakes in the grense configs would only
    surface via XSD validation."""
    fc = _query_features(rpformalgrense_provider_def)

    fmt = ReguleringsplanFormatter({"feature_type": "RpFormålGrense", "validate": True})
    gml = fmt.write({}, fc)

    _assert_envelope(gml, ReguleringsplanFormatter.SCHEMA_NAMESPACE, feature_count=1)

    assert "<app:RpFormålGrense " in gml
    assert "<app:lokalId>rpfg-smoke-001</app:lokalId>" in gml

    # kvalitet nested group (grense types carry it; no arealplanId)
    assert "<app:kvalitet>" in gml
    assert "<app:målemetode>24</app:målemetode>" in gml
    assert "<app:arealplanId>" not in gml

    # Line geometry through gml_passthrough into <app:grense>. With
    # gml_options: 1 (curve-aware, the flag-4-drop default) PostGIS emits
    # <gml:Curve>/<gml:LineStringSegment> rather than <gml:LineString> —
    # both satisfy gml:CurvePropertyType, but Curve is what production
    # produces.
    assert "<app:grense><gml:Curve" in gml
    assert "<gml:LineStringSegment>" in gml

    # gml:Curve is a geometry and gets the id; gml:LineStringSegment is a
    # curve segment, not a geometry, so it takes no gml:id.
    _, feature_id, geometry_id = gml_ids(gml)
    assert geometry_id == f"{feature_id}-0"
