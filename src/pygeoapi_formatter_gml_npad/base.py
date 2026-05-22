"""Shared GML 3.2.1 mechanics for all NPAD version formatters.

The :class:`_GMLBase` adapter wires pygeoapi's :class:`BaseFormatter`
contract to the SOSI GML writer infrastructure in
:mod:`pygeoapi_formatter_gml_npad.writer`. Subclasses declare class-level
constants for their (product spec, version) and the matching
``FEATURE_TYPES`` registry; ``write()`` is shared.
"""

import os
from functools import cached_property
from pathlib import Path

from pygeoapi.formatter.base import (
    BaseFormatter,
    FormatterGenericError,
    FormatterSerializationError,
)

from pygeoapi_formatter_gml_npad.mapping import FeatureTypeConfig, SchemaInfo
from pygeoapi_formatter_gml_npad.writer import (
    XML_FOOTER,
    build_nsmap,
    build_xml_header,
    serialize_feature,
)

GML_NAMESPACE = "http://www.opengis.net/gml/3.2"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"

_XSD_CACHE_DIR_ENV = "PYGEOAPI_GML_NPAD_XSD_CACHE_DIR"
_XSD_CACHE_DIR_DEFAULT = "/tmp/xsd-cache"


class _GMLBase(BaseFormatter):
    """Base for NPAD GML formatters.

    Subclasses must set:

    - ``SCHEMA_NAMESPACE``, ``SCHEMA_LOCATION``, ``SCHEMA_PREFIX``
    - ``FEATURE_TYPES``: dict mapping ``feature_type_name`` →
      :class:`FeatureTypeConfig`
    - ``_NAME``: short internal identifier passed to pygeoapi's
      :class:`BaseFormatter` (used by repr / logging, not routing)

    They may override ``DEFAULT_F`` and ``DEFAULT_MIMETYPE`` but the
    defaults here (``"gml"`` / ``"application/gml+xml"``) are the right
    starting point — see [[feedback-formatter-identifiers]] memory.
    """

    DEFAULT_F: str = "gml"
    DEFAULT_MIMETYPE: str = "application/gml+xml"

    SCHEMA_NAMESPACE: str = ""
    SCHEMA_LOCATION: str = ""
    SCHEMA_PREFIX: str = "app"

    FEATURE_TYPES: dict[str, FeatureTypeConfig] = {}
    _NAME: str = ""

    def __init__(self, formatter_def: dict):
        f = formatter_def.get("f", self.DEFAULT_F)
        mimetype = formatter_def.get("mimetype", self.DEFAULT_MIMETYPE)

        super().__init__({"name": self._NAME, "attachment": True})
        self.f = f
        self.mimetype = mimetype
        self.extension = "gml"

        # Validate feature_type at construction so misconfigured collections
        # fail at pygeoapi startup, not on first request.
        feature_type = formatter_def.get("feature_type")
        if not feature_type:
            raise FormatterGenericError(
                f"{type(self).__name__} requires 'feature_type' in "
                f"formatter_def; available: {sorted(self.FEATURE_TYPES)}"
            )
        if feature_type not in self.FEATURE_TYPES:
            raise FormatterGenericError(
                f"Unknown feature_type {feature_type!r} for "
                f"{type(self).__name__}; "
                f"available: {sorted(self.FEATURE_TYPES)}"
            )
        self._feature_type_name: str = feature_type
        self._validate: bool = bool(formatter_def.get("validate", True))

    @property
    def schema_info(self) -> SchemaInfo:
        return SchemaInfo(
            namespace=self.SCHEMA_NAMESPACE,
            schema_location=self.SCHEMA_LOCATION,
            prefix=self.SCHEMA_PREFIX,
        )

    @cached_property
    def _xsd_schema(self):
        # Lazy: avoids the XSD download at module-import or formatter
        # construction time. First request with validate=True triggers it.
        from pygeoapi_formatter_gml_npad.validation import load_xsd_schema

        cache_dir = Path(os.environ.get(_XSD_CACHE_DIR_ENV, _XSD_CACHE_DIR_DEFAULT))
        return load_xsd_schema(self.SCHEMA_LOCATION, cache_dir=cache_dir)

    def write(self, options: dict = {}, data: dict | None = None) -> str:
        config = self.FEATURE_TYPES[self._feature_type_name]

        features = (data or {}).get("features") or []
        rows: list[dict] = [(feat.get("properties") or {}) for feat in features]

        if self._validate and rows:
            from pygeoapi_formatter_gml_npad.validation import (
                validate_first_feature,
            )

            errors = validate_first_feature(
                rows[0], config, self.schema_info, self._xsd_schema
            )
            if errors:
                raise FormatterSerializationError(
                    f"First feature failed XSD validation against "
                    f"{self.SCHEMA_LOCATION}: {errors[:3]}"
                )

        nsmap = build_nsmap(self.schema_info)
        parts: list[str] = [
            build_xml_header(self.schema_info, nsmap, number_returned=len(rows))
        ]
        for i, row in enumerate(rows, start=1):
            parts.append(serialize_feature(row, config, self.SCHEMA_PREFIX, i))
        parts.append(XML_FOOTER)
        return "".join(parts)
