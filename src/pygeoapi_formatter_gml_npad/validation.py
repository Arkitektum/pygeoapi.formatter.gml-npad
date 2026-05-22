"""XSD schema loading and first-feature validation.

Downloads SOSI GML XSDs (with all dependencies), builds a local mirror
with rewritten ``schemaLocation`` paths, and validates individual feature
elements against the compiled schema.

Used both by the pygeoapi formatters (when ``validate=True`` is passed in
``formatter_def``) and by ``gml-export``'s first-feature validation in
the export pipeline.

Originally extracted from ``gml-export/src/gml_export/validation.py``.
"""

import logging
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

from lxml import etree

from .mapping import FeatureTypeConfig, SchemaInfo
from .writer import build_feature_member

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path("/tmp/xsd-cache")


def _url_to_path(url: str, base: Path) -> Path:
    """Convert a URL to a local filesystem path under ``base``."""
    parsed = urlparse(url)
    return base / parsed.netloc / parsed.path.lstrip("/")


def _download_all(
    url: str, download_dir: Path, visited: set[str] | None = None
) -> None:
    """Recursively download an XSD and all its imports/includes."""
    if visited is None:
        visited = set()
    if url in visited:
        return
    visited.add(url)

    cache_path = _url_to_path(url, download_dir)
    if not cache_path.exists():
        logger.debug(f"Downloading XSD: {url}")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = urlopen(url).read()  # noqa: S310
        cache_path.write_bytes(data)

    try:
        doc = etree.fromstring(cache_path.read_bytes())
    except etree.XMLSyntaxError:
        return

    xs_ns = "http://www.w3.org/2001/XMLSchema"
    for tag in [f"{{{xs_ns}}}import", f"{{{xs_ns}}}include"]:
        for elem in doc.iter(tag):
            loc = elem.get("schemaLocation")
            if not loc or not loc.startswith("http"):
                if loc:
                    resolved = urljoin(url, loc)
                    if resolved.startswith("http"):
                        _download_all(resolved, download_dir, visited)
                continue
            _download_all(loc, download_dir, visited)


def _build_local_mirror(download_dir: Path, local_dir: Path) -> None:
    """Copy downloaded XSDs to ``local_dir`` with ``schemaLocation`` URLs
    rewritten to local paths."""
    for src in download_dir.rglob("*.xsd"):
        rel = src.relative_to(download_dir)
        dst = local_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        content = src.read_text(encoding="utf-8")

        def replace_url(match: re.Match) -> str:
            url = match.group(1)
            if not url.startswith("http"):
                return match.group(0)
            local = _url_to_path(url, local_dir)
            if local.exists() or _url_to_path(url, download_dir).exists():
                return f'schemaLocation="{_url_to_path(url, local_dir)}"'
            return match.group(0)

        content = re.sub(r'schemaLocation="([^"]+)"', replace_url, content)
        dst.write_text(content, encoding="utf-8")


def load_xsd_schema(
    xsd_url: str,
    cache_dir: Path = DEFAULT_CACHE_DIR,
) -> etree.XMLSchema:
    """Download, mirror, and compile an XSD schema with all dependencies.

    Downloads are cached on disk; subsequent calls with the same URL skip
    the download phase.

    Returns a compiled :class:`lxml.etree.XMLSchema` ready for validation.
    """
    download_dir = cache_dir / "originals"
    local_dir = cache_dir / "local"

    logger.info(f"Loading XSD schema: {xsd_url}")
    _download_all(xsd_url, download_dir)
    _build_local_mirror(download_dir, local_dir)

    root_local = _url_to_path(xsd_url, local_dir)
    schema_doc = etree.parse(str(root_local))
    schema = etree.XMLSchema(schema_doc)
    logger.info("XSD schema loaded and compiled")

    return schema


def validate_first_feature(
    row: dict,
    config: FeatureTypeConfig,
    schema_info: SchemaInfo,
    xsd_schema: etree.XMLSchema,
) -> list[str]:
    """Validate a single feature built from a row against the XSD.

    Builds a feature-member element and validates the inner feature
    element (not the ``wfs:member`` wrapper) against the schema.

    Returns a list of validation error messages. Empty if valid.
    """
    member = build_feature_member(row, config, schema_info.namespace, feature_number=0)
    feature = member[0]

    if xsd_schema.validate(feature):
        return []

    errors = []
    seen: set[str] = set()
    for err in xsd_schema.error_log:
        short = err.message[:200]
        if short not in seen:
            seen.add(short)
            errors.append(err.message)

    return errors
