# pygeoapi.formatter.gml-npad

[pygeoapi](https://pygeoapi.io/) output formatters for **SOSI GML** under
the NPAD umbrella (*Nasjonal produktspesifikasjon for arealplan og digitalt
planregister*).

NPAD covers two distinct SOSI product specifications, each layered on GML
3.2.1. This package exposes one formatter per (product spec, version)
combination; shared GML mechanics live in
`pygeoapi_formatter_gml_npad.base`.

> **Status: scaffolding only.** GML serialization is not yet implemented.
> Each formatter's `write()` raises `NotImplementedError`.

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

### Single-version collection (defaults)

Register with defaults; clients request `?f=gml`:

```yaml
resources:
  reguleringsplaner_oslo:
    type: collection
    providers:
      - type: feature
        name: postgresql_ext.PostgreSQLExtendedProvider
        # ...
    formatters:
      - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
```

```
GET /collections/reguleringsplaner_oslo/items?f=gml
```

### Alias the current version under a stable, version-pinned `?f=`

Register the same formatter twice — defaults handle `?f=gml`, the second
registration adds `?f=gml-2019` as an explicit-version alias:

```yaml
formatters:
  - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
    # f='gml' (default — "give me current")
  - name: pygeoapi_formatter_gml_npad.reguleringsplan_20190401.ReguleringsplanFormatter
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
    mimetype: 'application/gml+xml; profile="reguleringsplan/20190401"'
```

This affects only the response `Content-Type` header. It does not change
which formatter pygeoapi dispatches to — that is always decided by `?f=`.

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
