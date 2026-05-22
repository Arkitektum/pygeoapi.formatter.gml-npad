import pytest

from pygeoapi_formatter_gml_npad.reguleringsplan_20190401 import (
    ReguleringsplanFormatter,
)


def test_default_identifiers():
    fmt = ReguleringsplanFormatter({})

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


def test_f_and_mimetype_overrides():
    fmt = ReguleringsplanFormatter(
        {"f": "gml-reg-2024", "mimetype": "application/gml+xml; profile=x"}
    )

    assert fmt.f == "gml-reg-2024"
    assert fmt.mimetype == "application/gml+xml; profile=x"
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_write_not_implemented():
    fmt = ReguleringsplanFormatter({})

    with pytest.raises(NotImplementedError):
        fmt.write({}, {"type": "FeatureCollection", "features": []})
