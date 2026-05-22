"""Kommuneplan (SOSI product spec, 20190401) output formatter."""

from pygeoapi_formatter_gml_npad.base import _GMLBase
from pygeoapi_formatter_gml_npad.kommuneplan_20190401.feature_types import (
    FEATURE_TYPES,
    SCHEMA_INFO,
)


class KommuneplanFormatter(_GMLBase):
    """SOSI GML formatter for the Kommuneplan product spec (20190401).

    Applies to collections backed by the ``kommuneplaner``,
    ``kommunedelplaner``, ``kommuneplanforslag`` and
    ``kommunedelplanforslag`` database families.

    Configuration in ``formatter_def``:

    - ``feature_type`` (required): SOSI feature type name, e.g.
      ``KpOmråde``. See ``FEATURE_TYPES`` for the full list.
    - ``f`` (optional): URL ``?f=`` value. Default ``"gml"``.
    - ``mimetype`` (optional): response Content-Type. Default
      ``"application/gml+xml"``.
    - ``validate`` (optional): if True (default), validate the first
      feature of each response against the XSD. Requires network access
      to skjema.geonorge.no on the first request (cached afterward).

    Provider contract: each feature's ``properties`` dict must use the
    dot-separated DB column names from the materialized views (e.g.
    ``identifikasjon.lokalId``, ``arealplanId.kommunenummer``) and carry
    pre-rendered geometry GML in ``_geometry_gml`` (and optionally
    ``_derived_point_gml``).
    """

    SCHEMA_NAMESPACE = SCHEMA_INFO.namespace
    SCHEMA_LOCATION = SCHEMA_INFO.schema_location
    SCHEMA_PREFIX = SCHEMA_INFO.prefix

    FEATURE_TYPES = FEATURE_TYPES
    _NAME = "gml-kommuneplan-20190401"

    def __repr__(self) -> str:
        return f"<KommuneplanFormatter> {self.name}"
