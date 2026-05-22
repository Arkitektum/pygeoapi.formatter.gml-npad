import pytest

from pygeoapi_formatter_gml_npad.npad_4_5_2 import NPAD452Formatter


def test_default_identifiers():
    fmt = NPAD452Formatter({})

    assert fmt.name == "gml-npad-4.5.2"
    assert fmt.f == "gml"
    assert fmt.mimetype == 'application/gml+xml; profile="npad/4.5.2"'
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_f_and_mimetype_overrides():
    fmt = NPAD452Formatter(
        {
            "f": "gml-npad-4",
            "mimetype": 'application/gml+xml; profile="custom"',
        }
    )

    assert fmt.f == "gml-npad-4"
    assert fmt.mimetype == 'application/gml+xml; profile="custom"'
    # Non-overridable identifiers keep their defaults
    assert fmt.extension == "gml"
    assert fmt.attachment is True


def test_write_not_implemented():
    fmt = NPAD452Formatter({})

    with pytest.raises(NotImplementedError):
        fmt.write({}, {"type": "FeatureCollection", "features": []})
