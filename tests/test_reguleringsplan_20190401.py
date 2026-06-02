import pytest
from pygeoapi.formatter.base import FormatterGenericError

from pygeoapi_formatter_gml_npad.reguleringsplan_20190401 import (
    FEATURE_TYPES,
    FEATURE_TYPES_BY_VIEW,
    SCHEMA_INFO,
    ReguleringsplanFormatter,
)


def test_default_identifiers():
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde"})

    assert fmt.name == "gml-reguleringsplan-20190401"
    assert fmt.f == "gml"
    assert fmt.mimetype == "application/gml+xml"
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_schema_constants():
    assert ReguleringsplanFormatter.SCHEMA_NAMESPACE == (
        "http://skjema.geonorge.no/SOSI/produktspesifikasjon/Reguleringsplan/20190401"
    )
    assert ReguleringsplanFormatter.SCHEMA_LOCATION == (
        "https://skjema.geonorge.no/SOSI/produktspesifikasjon/"
        "Reguleringsplan/20190401/reguleringsplan_20190401_filprod.xsd"
    )
    assert ReguleringsplanFormatter.SCHEMA_PREFIX == "app"


def test_schema_info_module_export():
    # SCHEMA_INFO is exported for external consumers (e.g. gml-export) and
    # must stay in sync with the formatter class's derived constants.
    assert SCHEMA_INFO.namespace == ReguleringsplanFormatter.SCHEMA_NAMESPACE
    assert SCHEMA_INFO.schema_location == ReguleringsplanFormatter.SCHEMA_LOCATION
    assert SCHEMA_INFO.prefix == ReguleringsplanFormatter.SCHEMA_PREFIX


def test_f_and_mimetype_overrides():
    fmt = ReguleringsplanFormatter(
        {
            "feature_type": "RpOmråde",
            "f": "gml-reg-2024",
            "mimetype": "application/gml+xml; profile=x",
        }
    )

    assert fmt.f == "gml-reg-2024"
    assert fmt.mimetype == "application/gml+xml; profile=x"
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_feature_types_registry_covers_known_types():
    # Spot-check a representative slice of the 38 RP feature types
    # (22 original + 16 grense)
    expected = {
        "RpOmråde",
        "RpArealformålOmråde",
        "RpJuridiskLinje",
        "RpPåskrift",
        "RbBevaringOmråde",
        "PblMidlByggAnleggOmråde",
        "RpGrense",
        "RpFormålGrense",
        "PblMidlByggAnleggGrense",
    }
    assert expected.issubset(FEATURE_TYPES.keys())
    assert len(FEATURE_TYPES) == 38


def test_grense_types_structure():
    """All grense types share one XSD shape: Fellesegenskaper_LinjerOgPunkt
    base sequence + a single `grense` element, and — unlike the line/point
    types — carry NO arealplanId group."""
    grense_types = [fc for name, fc in FEATURE_TYPES.items() if name.endswith("Grense")]
    assert len(grense_types) == 16

    from pygeoapi_formatter_gml_npad.mapping import GRENSE_PREFIX

    for fc in grense_types:
        assert fc.element_order == GRENSE_PREFIX + ["grense"], fc.feature_type_name
        assert fc.geometry_gml_name == "grense", fc.feature_type_name
        assert fc.geometry_column == "grense", fc.feature_type_name
        assert all(g.gml_parent != "arealplanId" for g in fc.nested_groups), (
            fc.feature_type_name
        )
        assert fc.view_name.endswith("_grense_mv"), fc.feature_type_name
        assert fc.id_prefix == fc.view_name.removesuffix("_grense_mv"), (
            fc.feature_type_name
        )


def test_write_serializes_minimal_grense_feature():
    fmt = ReguleringsplanFormatter(
        {"feature_type": "RpFormålGrense", "validate": False}
    )
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "grense-abc",
            "identifikasjon.navnerom": "ns",
            "identifikasjon.versjonId": "1",
            "_geometry_gml": (
                '<gml:LineString srsName="urn:ogc:def:crs:EPSG::25833">'
                "<gml:posList>597000 6643000 598000 6644000</gml:posList>"
                "</gml:LineString>"
            ),
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    assert "<app:RpFormålGrense " in out
    assert 'gml:id="rpformalgrense.1"' in out
    assert "<app:lokalId>grense-abc</app:lokalId>" in out
    assert "<app:grense><gml:LineString" in out
    assert 'gml:id="rpformalgrense.1.geom"' in out


def test_feature_types_by_view_index():
    assert len(FEATURE_TYPES_BY_VIEW) == len(FEATURE_TYPES)
    assert "rpomrade_omrade_mv" in FEATURE_TYPES_BY_VIEW
    assert FEATURE_TYPES_BY_VIEW["rpomrade_omrade_mv"].feature_type_name == "RpOmråde"
    # Every view-indexed config matches the feature-type-indexed one
    for view_name, fc in FEATURE_TYPES_BY_VIEW.items():
        assert FEATURE_TYPES[fc.feature_type_name] is fc
        assert fc.view_name == view_name


def test_init_without_feature_type_raises():
    # Misconfigured collections must fail at pygeoapi startup, not on the
    # first request.
    with pytest.raises(FormatterGenericError, match="feature_type"):
        ReguleringsplanFormatter({})


def test_init_with_unknown_feature_type_raises():
    with pytest.raises(FormatterGenericError, match="Unknown feature_type"):
        ReguleringsplanFormatter({"feature_type": "NotAThing"})


def test_write_empty_collection_skips_validation():
    # validate=True (default) but no rows → validation path is skipped,
    # so we don't need network access for this test.
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde"})
    out = fmt.write({}, {"type": "FeatureCollection", "features": []})

    assert out.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<wfs:FeatureCollection " in out
    assert 'numberReturned="0"' in out
    assert "</wfs:FeatureCollection>" in out
    assert ReguleringsplanFormatter.SCHEMA_NAMESPACE in out


def test_write_serializes_minimal_feature():
    # validate=False keeps this test offline (no XSD download).
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "validate": False})
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "abc-123",
            "identifikasjon.navnerom": "ns",
            "identifikasjon.versjonId": "1",
            "plantype": "35",
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    assert 'numberReturned="1"' in out
    assert "<app:RpOmråde " in out
    assert 'gml:id="rpomrade.1"' in out
    assert "<app:lokalId>abc-123</app:lokalId>" in out
    assert "<app:plantype>35</app:plantype>" in out


def test_nested_group_emits_default_value_when_all_source_columns_null():
    """Regression: a NestedGroup with ``default_values`` should still emit
    even when every source column for that group is NULL/missing in the
    row. Previously, ``_write_nested_group`` / ``_append_nested_group_str``
    short-circuited on ``has_value`` *before* consulting ``default_values``,
    which silently dropped defaulted-only elements that the XSD considers
    required.

    Exercised here via ``RpRegulertHøyde``'s ``HOYDEFRAPLANBESTEMMELSE``
    group, which defines a default for ``høydereferansesystem``.
    """
    fmt = ReguleringsplanFormatter(
        {"feature_type": "RpRegulertHøyde", "validate": False}
    )
    feature = {
        "type": "Feature",
        "properties": {
            # Required identifikasjon group
            "identifikasjon.lokalId": "rpregulerthoyde-1",
            "identifikasjon.navnerom": "ns",
            "identifikasjon.versjonId": "1",
            # All høydefraplanbestemmelse.* columns deliberately omitted.
            # The group should still appear thanks to default_values on
            # høydereferansesystem.
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    assert "<app:høydefraplanbestemmelse>" in out
    assert "<app:HøydeFraPlanbestemmelse>" in out
    assert "<app:høydereferansesystem>other: ukjent</app:høydereferansesystem>" in out
