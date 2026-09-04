import pytest
from pygeoapi.formatter.base import FormatterGenericError

from pygeoapi_formatter_gml_npad.reguleringsplan_20190401 import (
    FEATURE_TYPES,
    FEATURE_TYPES_BY_VIEW,
    SCHEMA_INFO,
    ReguleringsplanFormatter,
)
from pygeoapi_formatter_gml_npad.writer import (
    normalize_to_dotted,
    prepare_geometry_gml,
    urn_to_uri,
)
from tests.helpers import GML_ID_RE, gml_ids


def test_default_identifiers():
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde"})

    assert fmt.name == "gml-reguleringsplan-20190401"
    assert fmt.f == "gml"
    assert fmt.mimetype == "application/gml+xml"
    assert fmt.extension == "gml"
    # Default inline (matches pygeoapi BaseFormatter) — browsers render it.
    assert fmt.attachment is False


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
    assert fmt.attachment is False


def test_attachment_override_forces_download():
    # attachment: true → Content-Disposition: attachment, so the response
    # downloads as a file instead of rendering inline.
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "attachment": True})

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
    assert "<app:lokalId>grense-abc</app:lokalId>" in out
    assert "<app:grense><gml:LineString" in out

    # Collection id, feature id, geometry id — the geometry's is the
    # feature's plus '-0'.
    collection_id, feature_id, geometry_id = gml_ids(out)
    assert collection_id != feature_id
    assert geometry_id == f"{feature_id}-0"


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
    assert "<gml:FeatureCollection " in out
    assert "<gml:featureMember>" not in out
    assert "</gml:FeatureCollection>" in out
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

    assert out.count("<gml:featureMember>") == 1
    assert "<app:RpOmråde " in out
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


def test_normalize_to_dotted_flattens_nested_shape():
    """postgresql_ext ``property_shape: nested`` emits group columns as
    sub-dicts; the writer wants dot-joined keys. Flattening must be lossless
    and must leave parallel-array leaves (repeating groups) and synthetic
    string keys intact."""
    nested = {
        "identifikasjon": {"lokalId": "abc", "navnerom": "ns"},
        "utnytting": {"utnyttingstype": [1, 2], "utnyttingstall": [10, 20]},
        "plantype": "35",
        "_geometry_gml": "<gml:Polygon/>",
    }
    assert normalize_to_dotted(nested) == {
        "identifikasjon.lokalId": "abc",
        "identifikasjon.navnerom": "ns",
        # Repeating-group leaves stay as parallel arrays — exactly the
        # dotted form _write_repeating_nested_group already consumes.
        "utnytting.utnyttingstype": [1, 2],
        "utnytting.utnyttingstall": [10, 20],
        "plantype": "35",
        "_geometry_gml": "<gml:Polygon/>",
    }


def test_normalize_to_dotted_is_identity_on_dotted_shape():
    """``property_shape: dotted`` rows have no dict values, so normalization
    is a no-op — guarantees existing dotted deployments are unaffected."""
    dotted = {
        "identifikasjon.lokalId": "abc",
        "arealplanId.kommunenummer": "0301",
        "plantype": "35",
        "_geometry_gml": "<gml:Polygon/>",
    }
    assert normalize_to_dotted(dotted) == dotted


def test_write_accepts_nested_and_dotted_shapes_identically():
    """A collection on ``property_shape: nested`` (clean GeoJSON) and one on
    ``dotted`` must serialize identical GML — the contract that lets a single
    collection serve both ?f=json and ?f=gml. Identical up to the freshly
    minted ``gml:id`` values, which differ per document by design."""
    fmt = ReguleringsplanFormatter(
        {"feature_type": "RpFormålGrense", "validate": False}
    )
    geom = (
        '<gml:LineString srsName="urn:ogc:def:crs:EPSG::25833">'
        "<gml:posList>597000 6643000 598000 6644000</gml:posList>"
        "</gml:LineString>"
    )
    dotted_feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "grense-abc",
            "identifikasjon.navnerom": "ns",
            "identifikasjon.versjonId": "1",
            "kvalitet.målemetode": "24",
            "_geometry_gml": geom,
        },
    }
    nested_feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon": {
                "lokalId": "grense-abc",
                "navnerom": "ns",
                "versjonId": "1",
            },
            "kvalitet": {"målemetode": "24"},
            # Synthetic key stays top-level even in nested shape (matches
            # postgresql_ext's _create_feature behavior).
            "_geometry_gml": geom,
        },
    }

    dotted_out = fmt.write(
        {}, {"type": "FeatureCollection", "features": [dotted_feature]}
    )
    nested_out = fmt.write(
        {}, {"type": "FeatureCollection", "features": [nested_feature]}
    )

    assert GML_ID_RE.sub("gml:id=ID", nested_out) == GML_ID_RE.sub(
        "gml:id=ID", dotted_out
    )
    assert "<app:grense><gml:LineString" in nested_out
    assert "<app:målemetode>24</app:målemetode>" in nested_out


def test_every_gml_id_is_underscore_plus_uuid4():
    """Collection, feature and geometry ids are all '_' + lowercase UUID v4
    (geometries with a '-{serial}' suffix), and unique within the document."""
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "validate": False})
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "abc-123",
            "_geometry_gml": '<gml:Polygon srsName="urn:ogc:def:crs:EPSG::25833"/>',
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature, feature]})

    # 2 features × (feature id + geometry id) + the collection id
    ids = gml_ids(out)
    assert len(ids) == 5
    assert len(set(ids)) == 5
    # No id left over from any other scheme
    assert out.count("gml:id=") == 5


def test_geometry_ids_are_serial_within_the_feature_member():
    """Every geometry inside one feature member shares the feature's id with
    a '-{serial}' suffix, numbered from 0 in document order — sub-geometries
    included."""
    fmt = ReguleringsplanFormatter({"feature_type": "RpPåskrift", "validate": False})
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "abc-123",
            "_geometry_gml": (
                "<gml:MultiCurve><gml:curveMember><gml:LineString>"
                "<gml:posList>0 0 1 1</gml:posList>"
                "</gml:LineString></gml:curveMember></gml:MultiCurve>"
            ),
            # RpPåskrift also carries a derived point (objektposisjon), which
            # continues the same numbering.
            "_derived_point_gml": "<gml:Point><gml:pos>0 0</gml:pos></gml:Point>",
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    _, feature_id, *geometry_ids = gml_ids(out)
    assert geometry_ids == [
        f"{feature_id}-0",  # gml:MultiCurve
        f"{feature_id}-1",  # its member gml:LineString
        f"{feature_id}-2",  # gml:Point (objektposisjon)
    ]


def test_srs_name_urns_are_rewritten_to_uris():
    fmt = ReguleringsplanFormatter({"feature_type": "RpOmråde", "validate": False})
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "abc-123",
            "_geometry_gml": (
                '<gml:MultiSurface srsName="urn:ogc:def:crs:EPSG::25833">'
                '<gml:surfaceMember><gml:Polygon srsName="urn:ogc:def:crs:OGC::CRS84">'
                "<gml:exterior><gml:LinearRing/></gml:exterior>"
                "</gml:Polygon></gml:surfaceMember></gml:MultiSurface>"
            ),
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    assert "urn:ogc:def" not in out
    assert 'srsName="http://www.opengis.net/def/crs/EPSG/0/25833"' in out
    assert 'srsName="http://www.opengis.net/def/crs/OGC/0/CRS84"' in out


@pytest.mark.parametrize(
    ("urn", "expected"),
    [
        (
            "urn:ogc:def:crs:EPSG::25833",
            "http://www.opengis.net/def/crs/EPSG/0/25833",
        ),
        (
            "urn:ogc:def:crs:OGC::CRS84",
            "http://www.opengis.net/def/crs/OGC/0/CRS84",
        ),
        # A versioned URN keeps its version instead of getting the '0' default
        (
            "urn:ogc:def:crs:EPSG:9.9.1:4326",
            "http://www.opengis.net/def/crs/EPSG/9.9.1/4326",
        ),
        # Already a URI, or not an OGC URN at all → untouched
        (
            "http://www.opengis.net/def/crs/EPSG/0/25833",
            "http://www.opengis.net/def/crs/EPSG/0/25833",
        ),
        ("EPSG:25833", "EPSG:25833"),
    ],
)
def test_urn_to_uri(urn, expected):
    assert urn_to_uri(urn) == expected


def test_prepare_geometry_gml_skips_non_geometry_elements():
    """Rings, patches and property elements are not geometries in GML 3.2 and
    take no gml:id; the serial counter must not spend numbers on them."""
    fragment = (
        "<gml:Polygon><gml:exterior><gml:LinearRing>"
        "<gml:posList>0 0 1 0 1 1 0 0</gml:posList>"
        "</gml:LinearRing></gml:exterior></gml:Polygon>"
    )
    prepared, next_serial = prepare_geometry_gml(fragment, "_id", 0)

    assert prepared.count("gml:id=") == 1
    assert '<gml:Polygon gml:id="_id-0">' in prepared
    assert next_serial == 1


def test_prepare_geometry_gml_replaces_provider_supplied_ids():
    fragment = '<gml:Point gml:id="from-provider"><gml:pos>0 0</gml:pos></gml:Point>'
    prepared, next_serial = prepare_geometry_gml(fragment, "_id", 3)

    assert prepared == '<gml:Point gml:id="_id-3"><gml:pos>0 0</gml:pos></gml:Point>'
    assert next_serial == 4
