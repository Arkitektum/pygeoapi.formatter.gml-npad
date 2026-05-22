"""Kommuneplan (SOSI product spec, 20190401) output formatter."""

from pygeoapi_formatter_gml_npad.base import _GMLBase


class KommuneplanFormatter(_GMLBase):
    """SOSI GML formatter for the Kommuneplan product spec (20190401).

    Applies to collections backed by the ``kommuneplaner``,
    ``kommunedelplaner``, ``kommuneplanforslag`` and
    ``kommunedelplanforslag`` database families.

    ``f`` and ``mimetype`` can be overridden per-instance via
    ``formatter_def`` to support multi-version registration on a single
    collection during product-spec transition windows.
    """

    DEFAULT_F = "gml"
    DEFAULT_MIMETYPE = "application/gml+xml"

    SCHEMA_NAMESPACE = (
        "http://skjema.geonorge.no/SOSI/produktspesifikasjon/Kommuneplan/20190401"
    )
    SCHEMA_LOCATION = (
        "https://skjema.geonorge.no/SOSI/produktspesifikasjon/"
        "Kommuneplan/20190401/kommuneplan_20190401_filprod.xsd"
    )
    SCHEMA_PREFIX = "app"

    def __init__(self, formatter_def: dict):
        f = formatter_def.get("f", self.DEFAULT_F)
        mimetype = formatter_def.get("mimetype", self.DEFAULT_MIMETYPE)

        super().__init__({"name": "gml-kommuneplan-20190401", "attachment": True})
        self.f = f
        self.mimetype = mimetype
        self.extension = "gml"

    def write(self, options: dict = {}, data: dict | None = None) -> str:
        raise NotImplementedError(
            "Kommuneplan 20190401 GML serialization is not yet implemented."
        )

    def __repr__(self) -> str:
        return f"<KommuneplanFormatter> {self.name}"
