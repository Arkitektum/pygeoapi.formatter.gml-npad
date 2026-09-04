"""Shared assertions helpers for the formatter tests.

``gml:id`` values are minted per document (``_`` + lowercase UUID v4, with a
``-{serial}`` suffix on geometries), so tests match them by shape and by
their relationship to each other rather than by literal value.
"""

import re

UUID_RE = r"_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
GML_ID_RE = re.compile(rf'gml:id="({UUID_RE}(?:-\d+)?)"')


def gml_ids(xml: str) -> list[str]:
    """Every ``gml:id`` in ``xml``, in document order.

    The first is the collection's, then per feature member the feature's id
    followed by its geometries'.
    """
    return GML_ID_RE.findall(xml)
