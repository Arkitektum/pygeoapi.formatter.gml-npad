"""Shared GML 3.2.1 mechanics for all NPAD version formatters.

Subclasses set ``f``, ``mimetype``, ``extension``, ``attachment`` and
implement ``write()``. Common namespace bindings, envelope construction,
and geometry serialization helpers will land here once the NPAD schemas
are available.
"""

from pygeoapi.formatter.base import BaseFormatter

GML_NAMESPACE = "http://www.opengis.net/gml/3.2"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"


class _GMLBase(BaseFormatter):
    """Base for NPAD GML formatters. Stub until schemas land."""

    pass
