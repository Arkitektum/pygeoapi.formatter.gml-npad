import pytest
from pygeoapi.formatter.base import FormatterGenericError

from pygeoapi_formatter_gml_npad.kommuneplan_20190401 import (
    FEATURE_TYPES,
    FEATURE_TYPES_BY_VIEW,
    KommuneplanFormatter,
)


def test_default_identifiers():
    fmt = KommuneplanFormatter({"feature_type": "KpOmråde"})

    assert fmt.name == "gml-kommuneplan-20190401"
    assert fmt.f == "gml"
    assert fmt.mimetype == "application/gml+xml"
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_schema_constants():
    assert KommuneplanFormatter.SCHEMA_NAMESPACE == (
        "http://skjema.geonorge.no/SOSI/produktspesifikasjon/Kommuneplan/20190401"
    )
    assert KommuneplanFormatter.SCHEMA_LOCATION == (
        "https://skjema.geonorge.no/SOSI/produktspesifikasjon/"
        "Kommuneplan/20190401/kommuneplan_20190401_filprod.xsd"
    )
    assert KommuneplanFormatter.SCHEMA_PREFIX == "app"


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
    assert fmt.attachment is True


def test_feature_types_registry_covers_known_types():
    expected = {
        "KpOmråde",
        "KpArealformålOmråde",
        "KpJuridiskLinje",
        "KpPåskrift",
        "KpSamferdselLinje",
    }
    assert expected.issubset(FEATURE_TYPES.keys())
    assert len(FEATURE_TYPES) == 20


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
    assert 'gml:id="kpomrade.1"' in out
    assert "<app:lokalId>kp-xyz</app:lokalId>" in out
    assert "<app:plantype>20</app:plantype>" in out
