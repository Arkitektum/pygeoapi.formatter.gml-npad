import pytest

from pygeoapi_formatter_gml_npad.kommuneplan_20190401 import (
    KommuneplanFormatter,
)


def test_default_identifiers():
    fmt = KommuneplanFormatter({})

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
        {"f": "gml-kom-2024", "mimetype": "application/gml+xml; profile=x"}
    )

    assert fmt.f == "gml-kom-2024"
    assert fmt.mimetype == "application/gml+xml; profile=x"
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_write_not_implemented():
    fmt = KommuneplanFormatter({})

    with pytest.raises(NotImplementedError):
        fmt.write({}, {"type": "FeatureCollection", "features": []})
