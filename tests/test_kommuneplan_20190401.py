import pytest
from pygeoapi.formatter.base import FormatterGenericError

from pygeoapi_formatter_gml_npad.kommuneplan_20190401 import (
    FEATURE_TYPES,
    FEATURE_TYPES_BY_VIEW,
    SCHEMA_INFO,
    KommuneplanFormatter,
)


def test_default_identifiers():
    fmt = KommuneplanFormatter({"feature_type": "KpOmråde"})

    assert fmt.name == "gml-kommuneplan-20190401"
    assert fmt.f == "gml"
    assert fmt.mimetype == "application/gml+xml"
    assert fmt.extension == "gml"
    assert fmt.attachment is False


def test_schema_constants():
    assert KommuneplanFormatter.SCHEMA_NAMESPACE == (
        "http://skjema.geonorge.no/SOSI/produktspesifikasjon/Kommuneplan/20190401"
    )
    assert KommuneplanFormatter.SCHEMA_LOCATION == (
        "https://skjema.geonorge.no/SOSI/produktspesifikasjon/"
        "Kommuneplan/20190401/kommuneplan_20190401_filprod.xsd"
    )
    assert KommuneplanFormatter.SCHEMA_PREFIX == "app"


def test_schema_info_module_export():
    # SCHEMA_INFO is exported for external consumers (e.g. gml-export) and
    # must stay in sync with the formatter class's derived constants.
    assert SCHEMA_INFO.namespace == KommuneplanFormatter.SCHEMA_NAMESPACE
    assert SCHEMA_INFO.schema_location == KommuneplanFormatter.SCHEMA_LOCATION
    assert SCHEMA_INFO.prefix == KommuneplanFormatter.SCHEMA_PREFIX


def test_f_and_mimetype_overrides():
    fmt = KommuneplanFormatter(
        {
            "feature_type": "KpOmråde",
            "f": "gml-kom-2024",
            "mimetype": "application/gml+xml; profile=x",
        }
    )

    assert fmt.f == "gml-kom-2024"
    assert fmt.mimetype == "application/gml+xml; profile=x"
    assert fmt.extension == "gml"
    assert fmt.attachment is False


def test_feature_types_registry_covers_known_types():
    # 20 original + 13 grense
    expected = {
        "KpOmråde",
        "KpArealformålOmråde",
        "KpJuridiskLinje",
        "KpPåskrift",
        "KpSamferdselLinje",
        "KpGrense",
        "KpArealGrense",
    }
    assert expected.issubset(FEATURE_TYPES.keys())
    assert len(FEATURE_TYPES) == 33


def test_grense_types_structure():
    """KP grense types: same shared XSD shape as RP grense, with the KP
    conventions — DB geom column `geometri`, force_datetime kopidata."""
    grense_types = [fc for name, fc in FEATURE_TYPES.items() if name.endswith("Grense")]
    assert len(grense_types) == 13

    from pygeoapi_formatter_gml_npad.mapping import GRENSE_PREFIX

    for fc in grense_types:
        assert fc.element_order == GRENSE_PREFIX + ["grense"], fc.feature_type_name
        assert fc.geometry_gml_name == "grense", fc.feature_type_name
        assert fc.geometry_column == "geometri", fc.feature_type_name
        assert all(g.gml_parent != "arealplanId" for g in fc.nested_groups), (
            fc.feature_type_name
        )
        assert fc.id_prefix == fc.view_name.removesuffix("_mv"), fc.feature_type_name
        # KP kopidata variant: kopidato upgraded to xs:dateTime
        kopidata = next(g for g in fc.nested_groups if g.gml_parent == "kopidata")
        assert "kopidata.kopidato" in kopidata.force_datetime_columns, (
            fc.feature_type_name
        )


def test_write_serializes_minimal_grense_feature():
    fmt = KommuneplanFormatter({"feature_type": "KpGrense", "validate": False})
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "kp-grense-abc",
            "identifikasjon.navnerom": "ns",
            "identifikasjon.versjonId": "1",
            "_geometry_gml": (
                '<gml:LineString srsName="urn:ogc:def:crs:EPSG::25833">'
                "<gml:posList>598000 6644000 599000 6645000</gml:posList>"
                "</gml:LineString>"
            ),
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    assert "<app:KpGrense " in out
    assert 'gml:id="kpgrense.kp-grense-abc.1"' in out
    assert "<app:lokalId>kp-grense-abc</app:lokalId>" in out
    assert "<app:grense><gml:LineString" in out
    assert 'gml:id="kpgrense.kp-grense-abc.1.geom"' in out


def test_feature_types_by_view_index():
    assert len(FEATURE_TYPES_BY_VIEW) == len(FEATURE_TYPES)
    assert "kpomrade_mv" in FEATURE_TYPES_BY_VIEW
    assert FEATURE_TYPES_BY_VIEW["kpomrade_mv"].feature_type_name == "KpOmråde"
    for view_name, fc in FEATURE_TYPES_BY_VIEW.items():
        assert FEATURE_TYPES[fc.feature_type_name] is fc
        assert fc.view_name == view_name


def test_init_without_feature_type_raises():
    with pytest.raises(FormatterGenericError, match="feature_type"):
        KommuneplanFormatter({})


def test_init_with_unknown_feature_type_raises():
    with pytest.raises(FormatterGenericError, match="Unknown feature_type"):
        KommuneplanFormatter({"feature_type": "NotAThing"})


def test_write_empty_collection_skips_validation():
    fmt = KommuneplanFormatter({"feature_type": "KpOmråde"})
    out = fmt.write({}, {"type": "FeatureCollection", "features": []})

    assert out.startswith('<?xml version="1.0" encoding="utf-8"?>')
    assert "<wfs:FeatureCollection " in out
    assert 'numberReturned="0"' in out
    assert "</wfs:FeatureCollection>" in out
    assert KommuneplanFormatter.SCHEMA_NAMESPACE in out


def test_write_serializes_minimal_feature():
    fmt = KommuneplanFormatter({"feature_type": "KpOmråde", "validate": False})
    feature = {
        "type": "Feature",
        "properties": {
            "identifikasjon.lokalId": "kp-xyz",
            "identifikasjon.navnerom": "ns",
            "identifikasjon.versjonId": "1",
            "plantype": "20",
        },
    }
    out = fmt.write({}, {"type": "FeatureCollection", "features": [feature]})

    assert 'numberReturned="1"' in out
    assert "<app:KpOmråde " in out
    assert 'gml:id="kpomrade.kp-xyz.1"' in out
    assert "<app:lokalId>kp-xyz</app:lokalId>" in out
    assert "<app:plantype>20</app:plantype>" in out
