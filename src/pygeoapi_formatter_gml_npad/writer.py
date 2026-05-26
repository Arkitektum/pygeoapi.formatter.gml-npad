"""Streaming SOSI GML writer.

Generates schema-conformant SOSI GML 3.2 wrapped in a
``wfs:FeatureCollection``. Features are serialized via:

- :func:`build_feature_member` — lxml-based, used for XSD validation
- :func:`serialize_feature` — string-based, used in the hot path
- :func:`build_feature_collection` — the top-level entry point for
  pygeoapi-formatter callers (string in, string out)

Memory stays bounded regardless of feature count. Originally extracted
from ``gml-export/src/gml_export/gml_writer.py``.
"""

import gzip
import logging
import time
from collections.abc import Iterator
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as _xml_escape

from lxml import etree

from .mapping import FeatureTypeConfig, NestedGroup, SchemaInfo

logger = logging.getLogger(__name__)

# Standard namespaces
NS_WFS = "http://www.opengis.net/wfs/2.0"
NS_GML = "http://www.opengis.net/gml/3.2"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"


def _format_value(
    value: object,
    date_only: bool = False,
    zero_pad: int = 0,
    force_datetime: bool = False,
) -> str:
    """Format a database value for XML text content.

    - ``datetime`` → isoformat with ``T`` separator (``xs:dateTime``)
    - ``date_only=True`` → date part only, ``YYYY-MM-DD`` (``xs:date``)
    - ``force_datetime=True`` → date upgraded to ``xs:dateTime``
    - ``zero_pad > 0`` → left-pad with zeros to given width
    """
    if isinstance(value, datetime):
        if date_only:
            return value.date().isoformat()
        return value.isoformat()
    if isinstance(value, date):
        if force_datetime:
            return datetime(value.year, value.month, value.day).isoformat()
        return value.isoformat()
    text = str(value)
    if zero_pad > 0:
        return text.zfill(zero_pad)
    return text


def build_nsmap(schema: SchemaInfo) -> dict[str | None, str]:
    """Build the namespace map for the GML document."""
    return {
        "wfs": NS_WFS,
        "gml": NS_GML,
        schema.prefix: schema.namespace,
        "xsi": NS_XSI,
    }


def build_schema_location(schema: SchemaInfo) -> str:
    """Build the ``xsi:schemaLocation`` attribute value."""
    return f"{schema.namespace} {schema.schema_location}"


# ---------------------------------------------------------------------------
# lxml element-based builder (used for XSD validation of first feature)
# ---------------------------------------------------------------------------


def build_feature_member(
    row: dict,
    config: FeatureTypeConfig,
    app_ns: str,
    feature_number: int,
    nsmap: dict[str | None, str] | None = None,
) -> etree._Element:
    """Build a ``wfs:member`` element containing one SOSI GML feature.

    Used for XSD validation of the first feature per view. The export
    hot path uses :func:`serialize_feature` instead.
    """
    member = etree.Element(f"{{{NS_WFS}}}member", nsmap=nsmap)

    gml_id = f"{config.id_prefix}.{feature_number}"
    feature = etree.SubElement(
        member,
        f"{{{app_ns}}}{config.feature_type_name}",
        attrib={f"{{{NS_GML}}}id": gml_id},
    )

    if config.element_order:
        nested_by_name = {g.gml_parent: g for g in config.nested_groups}
        simple_by_gml_name = {
            gml_name: db_col for db_col, gml_name in config.simple_properties.items()
        }

        for gml_name in config.element_order:
            if gml_name == config.geometry_gml_name:
                _write_geometry(feature, row, config, app_ns, gml_id)
            elif gml_name == config.derived_point_geometry:
                _write_derived_point(feature, row, gml_name, app_ns, gml_id)
            elif gml_name in nested_by_name:
                _write_nested_group(feature, nested_by_name[gml_name], row, app_ns)
            elif gml_name in simple_by_gml_name:
                db_col = simple_by_gml_name[gml_name]
                value = row.get(db_col)
                if value is None:
                    value = config.default_values.get(db_col)
                if value is not None:
                    prop = etree.SubElement(feature, f"{{{app_ns}}}{gml_name}")
                    prop.text = _format_value(value)
    else:
        for group in config.nested_groups:
            _write_nested_group(feature, group, row, app_ns)
        for db_col, gml_name in config.simple_properties.items():
            value = row.get(db_col)
            if value is None:
                value = config.default_values.get(db_col)
            if value is not None:
                prop = etree.SubElement(feature, f"{{{app_ns}}}{gml_name}")
                prop.text = _format_value(value)
        _write_geometry(feature, row, config, app_ns, gml_id)

    return member


def _write_geometry(
    parent: etree._Element,
    row: dict,
    config: FeatureTypeConfig,
    app_ns: str,
    gml_id: str,
) -> None:
    """Write the geometry element from ST_AsGML output."""
    geom_gml = row.get("_geometry_gml")
    if not geom_gml:
        return

    geom_wrapper = etree.SubElement(parent, f"{{{app_ns}}}{config.geometry_gml_name}")
    try:
        wrapped = f'<_g xmlns:gml="{NS_GML}">{geom_gml}</_g>'
        dummy = etree.fromstring(wrapped.encode("utf-8"))
        geom_elem = dummy[0]
        geom_elem.set(f"{{{NS_GML}}}id", f"{gml_id}.geom")
        geom_wrapper.append(geom_elem)
    except etree.XMLSyntaxError:
        logger.warning(
            f"Invalid GML geometry for {config.view_name} "
            f"objid={row.get('objid')}, skipping geometry"
        )


def _write_derived_point(
    parent: etree._Element,
    row: dict,
    gml_name: str,
    app_ns: str,
    gml_id: str,
) -> None:
    """Write a point geometry derived from the primary geometry."""
    geom_gml = row.get("_derived_point_gml")
    if not geom_gml:
        return

    wrapper = etree.SubElement(parent, f"{{{app_ns}}}{gml_name}")
    try:
        wrapped = f'<_g xmlns:gml="{NS_GML}">{geom_gml}</_g>'
        dummy = etree.fromstring(wrapped.encode("utf-8"))
        geom_elem = dummy[0]
        geom_elem.set(f"{{{NS_GML}}}id", f"{gml_id}.{gml_name}")
        wrapper.append(geom_elem)
    except etree.XMLSyntaxError:
        logger.warning(
            f"Invalid derived point GML for objid={row.get('objid')}, "
            f"skipping {gml_name}"
        )


def _write_nested_group(
    parent: etree._Element,
    group: NestedGroup,
    row: dict,
    app_ns: str,
) -> None:
    """Write a nested element group (lxml version for validation)."""
    if group.repeating:
        _write_repeating_nested_group(parent, group, row, app_ns)
        return

    # A defaulted column counts toward "the group has value" — otherwise
    # groups whose source columns are all NULL get skipped here even when
    # default_values would have populated them inside the loop below.
    has_value = any(
        row.get(db_col) is not None or db_col in group.default_values
        for db_col in group.columns
    )
    if not has_value:
        return

    if group.required_columns:
        if any(row.get(col) is None for col in group.required_columns):
            return

    outer = etree.SubElement(parent, f"{{{app_ns}}}{group.gml_parent}")
    wrapper = etree.SubElement(outer, f"{{{app_ns}}}{group.gml_wrapper_type}")

    for db_col, gml_name in group.columns.items():
        value = row.get(db_col)
        if value is None:
            value = group.default_values.get(db_col)
        if value is not None:
            child = etree.SubElement(wrapper, f"{{{app_ns}}}{gml_name}")
            child.text = _format_value(
                value,
                date_only=(db_col in group.date_only_columns),
                zero_pad=group.zero_pad_columns.get(db_col, 0),
                force_datetime=(db_col in group.force_datetime_columns),
            )


def _write_repeating_nested_group(
    parent: etree._Element,
    group: NestedGroup,
    row: dict,
    app_ns: str,
) -> None:
    """Write multiple instances of a nested group (lxml version for validation)."""
    col_items = list(group.columns.items())
    arrays: dict[str, list] = {}
    max_len = 0
    for db_col, _ in col_items:
        val = row.get(db_col)
        if isinstance(val, list):
            arrays[db_col] = val
            max_len = max(max_len, len(val))
        elif val is not None:
            arrays[db_col] = [val]
            max_len = max(max_len, 1)

    for i in range(max_len):
        outer = etree.SubElement(parent, f"{{{app_ns}}}{group.gml_parent}")
        wrapper = etree.SubElement(outer, f"{{{app_ns}}}{group.gml_wrapper_type}")

        for db_col, gml_name in col_items:
            arr = arrays.get(db_col)
            if arr is None or i >= len(arr):
                continue
            value = arr[i]
            if value is not None:
                child = etree.SubElement(wrapper, f"{{{app_ns}}}{gml_name}")
                child.text = _format_value(
                    value,
                    date_only=(db_col in group.date_only_columns),
                    zero_pad=group.zero_pad_columns.get(db_col, 0),
                    force_datetime=(db_col in group.force_datetime_columns),
                )


# ---------------------------------------------------------------------------
# String-based serializer (hot path — no lxml overhead)
# ---------------------------------------------------------------------------


def _inject_gml_id(geom_gml: str, gml_id: str) -> str:
    """Inject a ``gml:id`` attribute into the first opening tag of a GML fragment."""
    idx = geom_gml.index(">")
    return f'{geom_gml[:idx]} gml:id="{gml_id}"{geom_gml[idx:]}'


def _fmt(value: object, group: NestedGroup, db_col: str) -> str:
    """Format + XML-escape a nested-group column value."""
    return _xml_escape(
        _format_value(
            value,
            date_only=(db_col in group.date_only_columns),
            zero_pad=group.zero_pad_columns.get(db_col, 0),
            force_datetime=(db_col in group.force_datetime_columns),
        )
    )


def _append_geometry_str(
    parts: list[str],
    row: dict,
    geometry_gml_name: str,
    prefix: str,
    gml_id: str,
) -> None:
    geom_gml = row.get("_geometry_gml")
    if not geom_gml:
        return
    try:
        injected = _inject_gml_id(geom_gml, f"{gml_id}.geom")
        parts.append(
            f"<{prefix}:{geometry_gml_name}>{injected}</{prefix}:{geometry_gml_name}>"
        )
    except (ValueError, IndexError):
        pass


def _append_derived_point_str(
    parts: list[str],
    row: dict,
    gml_name: str,
    prefix: str,
    gml_id: str,
) -> None:
    geom_gml = row.get("_derived_point_gml")
    if not geom_gml:
        return
    try:
        injected = _inject_gml_id(geom_gml, f"{gml_id}.{gml_name}")
        parts.append(f"<{prefix}:{gml_name}>{injected}</{prefix}:{gml_name}>")
    except (ValueError, IndexError):
        pass


def _append_nested_group_str(
    parts: list[str],
    group: NestedGroup,
    row: dict,
    prefix: str,
) -> None:
    if group.repeating:
        _append_repeating_nested_group_str(parts, group, row, prefix)
        return

    # Mirror of _write_nested_group: defaulted columns count toward
    # "the group has value", so groups that exist solely to emit
    # defaults aren't dropped at the early-return.
    has_value = any(
        row.get(db_col) is not None or db_col in group.default_values
        for db_col in group.columns
    )
    if not has_value:
        return

    if group.required_columns:
        if any(row.get(col) is None for col in group.required_columns):
            return

    parts.append(f"<{prefix}:{group.gml_parent}><{prefix}:{group.gml_wrapper_type}>")

    for db_col, gml_name in group.columns.items():
        value = row.get(db_col)
        if value is None:
            value = group.default_values.get(db_col)
        if value is not None:
            parts.append(
                f"<{prefix}:{gml_name}>{_fmt(value, group, db_col)}</{prefix}:{gml_name}>"
            )

    parts.append(f"</{prefix}:{group.gml_wrapper_type}></{prefix}:{group.gml_parent}>")


def _append_repeating_nested_group_str(
    parts: list[str],
    group: NestedGroup,
    row: dict,
    prefix: str,
) -> None:
    col_items = list(group.columns.items())
    arrays: dict[str, list] = {}
    max_len = 0
    for db_col, _ in col_items:
        val = row.get(db_col)
        if isinstance(val, list):
            arrays[db_col] = val
            max_len = max(max_len, len(val))
        elif val is not None:
            arrays[db_col] = [val]
            max_len = max(max_len, 1)

    for i in range(max_len):
        parts.append(
            f"<{prefix}:{group.gml_parent}><{prefix}:{group.gml_wrapper_type}>"
        )
        for db_col, gml_name in col_items:
            arr = arrays.get(db_col)
            if arr is None or i >= len(arr):
                continue
            value = arr[i]
            if value is not None:
                parts.append(
                    f"<{prefix}:{gml_name}>{_fmt(value, group, db_col)}</{prefix}:{gml_name}>"
                )
        parts.append(
            f"</{prefix}:{group.gml_wrapper_type}></{prefix}:{group.gml_parent}>"
        )


def serialize_feature(
    row: dict,
    config: FeatureTypeConfig,
    prefix: str,
    feature_number: int,
) -> str:
    """Serialize one feature to an XML string (no lxml).

    Namespace prefixes must match those declared on the parent
    ``FeatureCollection``.
    """
    p = prefix
    gml_id = f"{config.id_prefix}.{feature_number}"
    parts: list[str] = [
        f'<wfs:member><{p}:{config.feature_type_name} gml:id="{gml_id}">'
    ]

    if config.element_order:
        nested_by_name = {g.gml_parent: g for g in config.nested_groups}
        simple_by_gml = {gml: db for db, gml in config.simple_properties.items()}

        for gml_name in config.element_order:
            if gml_name == config.geometry_gml_name:
                _append_geometry_str(parts, row, config.geometry_gml_name, p, gml_id)
            elif gml_name == config.derived_point_geometry:
                _append_derived_point_str(parts, row, gml_name, p, gml_id)
            elif gml_name in nested_by_name:
                _append_nested_group_str(parts, nested_by_name[gml_name], row, p)
            elif gml_name in simple_by_gml:
                db_col = simple_by_gml[gml_name]
                value = row.get(db_col)
                if value is None:
                    value = config.default_values.get(db_col)
                if value is not None:
                    parts.append(
                        f"<{p}:{gml_name}>{_xml_escape(_format_value(value))}</{p}:{gml_name}>"
                    )
    else:
        for group in config.nested_groups:
            _append_nested_group_str(parts, group, row, p)
        for db_col, gml_name in config.simple_properties.items():
            value = row.get(db_col)
            if value is None:
                value = config.default_values.get(db_col)
            if value is not None:
                parts.append(
                    f"<{p}:{gml_name}>{_xml_escape(_format_value(value))}</{p}:{gml_name}>"
                )
        _append_geometry_str(parts, row, config.geometry_gml_name, p, gml_id)

    parts.append(f"</{p}:{config.feature_type_name}></wfs:member>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Top-level builders
# ---------------------------------------------------------------------------


def build_xml_header(
    schema: SchemaInfo,
    nsmap: dict[str | None, str],
    number_returned: int | str = "unknown",
    number_matched: int | str = "unknown",
) -> str:
    """Build the XML declaration and opening ``wfs:FeatureCollection`` tag.

    ``number_returned`` defaults to ``"unknown"``; pygeoapi callers pass
    the actual feature count. ``number_matched`` stays ``"unknown"``
    unless the caller knows the underlying collection size.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    schema_location = build_schema_location(schema)

    ns_decls = []
    for prefix, uri in nsmap.items():
        if prefix is None:
            ns_decls.append(f'xmlns="{uri}"')
        else:
            ns_decls.append(f'xmlns:{prefix}="{uri}"')

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f"<wfs:FeatureCollection {' '.join(ns_decls)}"
        f' xsi:schemaLocation="{schema_location}"'
        f' timeStamp="{timestamp}"'
        f' numberMatched="{number_matched}"'
        f' numberReturned="{number_returned}">'
    )


XML_FOOTER = "</wfs:FeatureCollection>"


def build_feature_collection(
    rows: list[dict],
    config: FeatureTypeConfig,
    schema: SchemaInfo,
) -> str:
    """Serialize a list of row dicts to a complete GML FeatureCollection.

    Entry point used by the pygeoapi formatter. Each row is a flat dict
    keyed by dot-separated DB column names (e.g. ``identifikasjon.lokalId``)
    plus optional ``_geometry_gml`` and ``_derived_point_gml`` keys
    holding pre-rendered GML fragments.
    """
    nsmap = build_nsmap(schema)
    prefix = schema.prefix

    parts: list[str] = [build_xml_header(schema, nsmap, number_returned=len(rows))]
    for i, row in enumerate(rows, start=1):
        parts.append(serialize_feature(row, config, prefix, i))
    parts.append(XML_FOOTER)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Streaming gzip export orchestrator (used by gml-export, not by pygeoapi)
# ---------------------------------------------------------------------------


def export_view_to_gml(
    row_batches: Iterator[list[dict]],
    config: FeatureTypeConfig,
    schema: SchemaInfo,
    output_path: Path,
) -> int:
    """Export a materialized view to a gzip-compressed SOSI GML file.

    Uses string-based serialization in the hot loop to avoid lxml element
    construction and XML parsing overhead. Memory stays bounded: one
    feature string at a time.

    Kept for use by ``gml-export``; pygeoapi callers should use
    :func:`build_feature_collection` instead.

    Returns the number of features written.
    """
    nsmap = build_nsmap(schema)
    prefix = schema.prefix

    feature_count = 0
    fetch_time = 0.0
    write_time = 0.0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with gzip.open(output_path, "wb", compresslevel=1) as gz:
        gz.write(build_xml_header(schema, nsmap, number_returned=0).encode("utf-8"))

        while True:
            t0 = time.monotonic()
            batch = next(row_batches, None)
            fetch_time += time.monotonic() - t0

            if batch is None:
                break

            t1 = time.monotonic()
            for row in batch:
                feature_count += 1
                gz.write(
                    serialize_feature(row, config, prefix, feature_count).encode(
                        "utf-8"
                    )
                )
            write_time += time.monotonic() - t1

        gz.write(XML_FOOTER.encode("utf-8"))

    logger.info(
        f"Wrote {feature_count} features to {output_path.name} "
        f"({output_path.stat().st_size / 1024 / 1024:.1f} MB compressed) "
        f"[fetch={fetch_time:.1f}s, write={write_time:.1f}s]"
    )
    return feature_count
