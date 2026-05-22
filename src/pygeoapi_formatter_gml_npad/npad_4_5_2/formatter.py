"""NPAD 4.5.2 output formatter (GML serialization pending schema delivery)."""

from pygeoapi_formatter_gml_npad.base import _GMLBase


class NPAD452Formatter(_GMLBase):
    """SOSI-GML NPAD 4.5.2 output formatter.

    ``f`` and ``mimetype`` can be overridden per-instance via
    ``formatter_def`` so a collection can register multiple NPAD versions
    without colliding on the same ``?f=`` value.
    """

    DEFAULT_F = "gml"
    DEFAULT_MIMETYPE = 'application/gml+xml; profile="npad/4.5.2"'

    def __init__(self, formatter_def: dict):
        f = formatter_def.get("f", self.DEFAULT_F)
        mimetype = formatter_def.get("mimetype", self.DEFAULT_MIMETYPE)

        super().__init__({"name": "gml-npad-4.5.2", "attachment": True})
        self.f = f
        self.mimetype = mimetype
        self.extension = "gml"

    def write(self, options: dict = {}, data: dict | None = None) -> str:
        raise NotImplementedError(
            "NPAD 4.5.2 GML serialization is not yet implemented; "
            "awaiting NPAD 4.5.2 schema delivery."
        )

    def __repr__(self) -> str:
        return f"<NPAD452Formatter> {self.name}"
