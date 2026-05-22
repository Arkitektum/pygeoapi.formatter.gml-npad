# pygeoapi.formatter.gml-npad

[pygeoapi](https://pygeoapi.io/) output formatters for **SOSI GML** under
the NPAD umbrella (*Nasjonal produktspesifikasjon for arealplan og digitalt
planregister*).

NPAD covers two distinct SOSI product specifications, each layered on GML
3.2.1. This package exposes one formatter per (product spec, version)
combination; shared GML mechanics live in
`pygeoapi_formatter_gml_npad.base`.

> **Status: writer implemented, no published release yet.** Each
> formatter's `write()` produces schema-conformant SOSI GML; the writer
> infrastructure was ported from `DiBK.Oppsamlingsregister/nap/gml-export`
> as part of an in-progress dependency inversion.

## Supported product specs

| Product spec    | Version    | Class                      | Subpackage                                               |
| --------------- | ---------- | -------------------------- | -------------------------------------------------------- |
| Reguleringsplan | 20190401   | `ReguleringsplanFormatter` | `pygeoapi_formatter_gml_npad.reguleringsplan_20190401`   |
| Kommuneplan     | 20190401   | `KommuneplanFormatter`     | `pygeoapi_formatter_gml_npad.kommuneplan_20190401`       |

Defaults for every formatter: `f='gml'`, `mimetype='application/gml+xml'`,
`extension='gml'`, `attachment=True`. The product-spec version is conveyed
**in the response body** via `xmlns` and `xsi:schemaLocation`, not the
`Content-Type` header — clients that need to verify the version should
read the body, not negotiate.

When new product-spec revisions arrive, they land as sibling subpackages
(`reguleringsplan_<new_date>/`, etc.). Existing imports never change
meaning. See [Future versions](#future-versions) below for the migration
recipe.

## Which formatter goes on which collection

Pick the formatter that matches the collection's data source database:

| Database name                                                          | Formatter                  |
| ---------------------------------------------------------------------- | -------------------------- |
| `reguleringsplaner`, `reguleringsplanforslag`                          | `ReguleringsplanFormatter` |
| `kommuneplaner`, `kommunedelplaner`, `kommuneplanforslag`, `kommunedelplanforslag` | `KommuneplanFormatter`     |

A single collection cannot mix Reguleringsplan and Kommuneplan data — the
schemas have different namespaces and feature sets.

## Installation

Installed via git in consuming Dockerfiles (no PyPI release):

```dockerfile
RUN uv pip install git+https://github.com/Arkitektum/pygeoapi.formatter.gml-npad@main
```

For local development:

```bash
pip install -e .[dev]
pytest
ruff check .
```

## pygeoapi configuration

### Required: tell the formatter which SOSI feature type to serialize

Each collection serves one SOSI feature type (`RpOmråde`,
`KpArealformålOmråde`, etc.). The formatter is told via the
`feature_type` field on the YAML registration. The full list of
supported names lives in each subpackage's
`feature_types.FEATURE_TYPES` dict (22 for Reguleringsplan, 20 for
Kommuneplan).

### Single-version collection

```yaml
resources:
  reguleringsplaner_oslo_rpomrade:
    type: collection
    providers:
      - type: feature
        name: postgresql_ext.PostgreSQLExtendedProvider
        # ...
    formatters:
      - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
        feature_type: RpOmråde
```

```
GET /collections/reguleringsplaner_oslo_rpomrade/items?f=gml
```

### Alias the current version under a stable, version-pinned `?f=`

Register the same formatter twice — defaults handle `?f=gml`, the second
registration adds `?f=gml-2019` as an explicit-version alias:

```yaml
formatters:
  - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
    feature_type: RpOmråde
    # f='gml' (default — "give me current")
  - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
    feature_type: RpOmråde
    f: gml-2019
```

Both produce identical bytes. Clients that want to pin to a specific
version can do so today — long before any newer version exists — and stay
unaffected by future canonical flips.

### Overriding `mimetype` (operator escape hatch)

The `mimetype` field on a formatter entry overrides the default
`application/gml+xml`. Useful when:

- An OGC conformance suite or schema validator demands a `profile=` parameter
- An OpenAPI generator or proxy needs distinct Content-Type strings per registration
- A deployment wants `charset=utf-8` or other parameters spelled out

```yaml
formatters:
  - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
    feature_type: RpOmråde
    mimetype: 'application/gml+xml; profile="reguleringsplan/20190401"'
```

This affects only the response `Content-Type` header. It does not change
which formatter pygeoapi dispatches to — that is always decided by `?f=`.

### XSD validation (`validate`)

By default, the formatter validates the **first feature** of each
response against the XSD (downloaded once from `skjema.geonorge.no`,
cached on disk). It catches data-driven writer bugs without paying
validation cost on every feature.

```yaml
formatters:
  - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
    feature_type: RpOmråde
    validate: false   # opt out — trust the writer, skip the XSD round-trip
```

The first request with `validate: true` takes a few seconds while the
XSD bundle downloads. A future release will bundle XSDs in the package
to remove the cold-start cost; until then, deployments that can't reach
`skjema.geonorge.no` at runtime should set `validate: false` and rely
on CI-time validation.

Cache directory defaults to `/tmp/xsd-cache`. Override with the
environment variable `PYGEOAPI_GML_NPAD_XSD_CACHE_DIR` to a persistent
location for long-running pygeoapi workers (recommended):

```bash
export PYGEOAPI_GML_NPAD_XSD_CACHE_DIR=/var/lib/pygeoapi/xsd-cache
```

### Provider data-shape contract

The formatter is **strict** about its input shape. Each feature's
`properties` dict must use the raw materialized-view column names —
dots and Norwegian characters preserved — plus pre-rendered geometry
GML strings:

```python
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "identifikasjon.lokalId": "abc-123",
                "identifikasjon.navnerom": "...",
                "arealplanId.kommunenummer": "0301",
                "førsteDigitaliseringsdato": "2018-06-12",
                "kvalitet.målemetode": "24",
                "plantype": "35",
                # ... other dot-separated columns ...
                "_geometry_gml": "<gml:Polygon ...>...</gml:Polygon>",
                "_derived_point_gml": "<gml:Point ...>",  # RpPåskrift only
            },
        },
    ],
}
```

Specifically:

- **Property keys are dot-bearing, case- and diacritic-preserving.**
  Neither of pygeoapi's two built-in property modes preserves this
  shape: `flatten_properties: true` strips the prefix
  (`identifikasjon.lokalId` → `lokalId`, with silent collisions when
  two columns share a leaf — e.g. `arealplanId.kommunenummer` vs
  `bygning.kommunenummer`), and `flatten_properties: false`
  (canonical) nests them as
  `{"identifikasjon": {"lokalId": "..."}}`. To produce the verbatim
  dotted shape this formatter needs, use Arkitektum's
  `postgresql_ext` provider with `property_shape: dotted` (the exact
  flag name is being finalized between the formatter and provider
  agents — see deployment docs at cutover time).
- **Values are native Python types from psycopg**: `str`, `int`,
  `float`, `datetime.date`, `datetime.datetime`, `None`, and `list`
  for repeating nested groups (PostgreSQL array columns).
- **`_geometry_gml` is a raw GML 3.2 XML string** from
  `ST_AsGML(3, geom, 15, 1|4)` (flag `1` = long CRS URN, flag `4` =
  `<LineString>` rather than `<Curve>`). Single-component
  multi-geometries **must be unwrapped server-side** —
  `MultiPolygon` with one ring and `MultiLineString` with one part
  must arrive as their inner `Polygon` / `LineString`. The SOSI XSDs
  reject `Multi*` wrappers in `gml:SurfacePropertyType` etc., so the
  unwrap belongs in the SQL (`CASE WHEN ST_NumGeometries(...) = 1
  THEN ST_GeometryN(...) ELSE ... END`), not the formatter.
- **`_derived_point_gml` is a raw GML 3.2 `<Point>` string**, required
  only for `RpPåskrift` (the XSD demands a separate point alongside
  the primary line geometry). The provider computes it as
  "start point for lines, passthrough for points" via `ST_PointN`.
- **`objid` is ignored** if present — the formatter generates
  `gml:id` from a monotonic counter via the feature type's
  `id_prefix`.

The Reguleringsplan subpackage also hosts the **Rb\*** and
**PblMidlByggAnleggOmråde** feature types — they share the
Reguleringsplan namespace and XSD, despite the prefix suggesting
otherwise. Look in `reguleringsplan_20190401.FEATURE_TYPES` for the
full list.

This shape matches the materialized views used by
`pygeoapi.plandata`'s `postgresql_ext` provider. The provider is
responsible for `ST_AsGML` rendering and Multi-unwrap; the formatter
trusts what it receives.

### A note on `Accept`-header negotiation

`Accept`-header content negotiation cannot reliably discriminate between
versions on a collection that registers multiple instances. pygeoapi's
format dispatch matches on the bare media type but does not consider
parameters (e.g. `profile=...`). Use `?f=` for deterministic selection.

## Future versions

When a new product-spec revision is published (call it `<new_date>`):

**Step 1 — add a sibling subpackage** in this repo:

```
src/pygeoapi_formatter_gml_npad/
├── reguleringsplan_20190401/        # existing, unchanged
└── reguleringsplan_<new_date>/      # new sibling
```

Existing imports keep working forever. The version is locked into the
import path, so `from pygeoapi_formatter_gml_npad.reguleringsplan_20190401`
never silently changes meaning.

**Step 2 — phased rollout per collection.** The deployment operator
controls when `?f=gml` flips to the new version. Clients that pinned to
`?f=gml-2019` (per the alias pattern above) never break.

| Phase                                        | Registrations on the collection                                            | `?f=gml` | `?f=gml-2019` | `?f=gml-v2` |
| -------------------------------------------- | -------------------------------------------------------------------------- | -------- | ------------- | ----------- |
| Today (just 2019)                            | `_20190401` → `f=gml`                                                      | 2019     | 404           | 404         |
| Introduce explicit alias                     | `_20190401` × 2 → `f=gml` + `f=gml-2019`                                   | 2019     | 2019          | 404         |
| New version drops, 2019 still canonical      | `_20190401` × 2 + `_<new_date>` → `f=gml-v2`                               | 2019     | 2019          | new         |
| Canonical flips to new version               | `_20190401` → `f=gml-2019`; `_<new_date>` × 2 → `f=gml` + `f=gml-v2`       | new      | 2019          | new         |
| Drop 2019 entirely                           | `_<new_date>` × 2 → `f=gml` + `f=gml-v2`                                   | new      | gone          | new         |

Clients pinned to `?f=gml-2019` from the second phase onwards never see a
breaking change until the deployment explicitly retires 2019 in the last
phase. The retirement is a deliberate, visible config change — not a
silent flip.

## License

MIT — see [LICENSE](LICENSE).
