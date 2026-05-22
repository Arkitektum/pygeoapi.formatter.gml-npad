# pygeoapi.formatter.gml-npad

[pygeoapi](https://pygeoapi.io/) output formatter for **SOSI-GML NPAD**
(*Nasjonal produktspesifikasjon for arealplan og digitalt planregister*).

One repo, one distribution, one NPAD version per subpackage. NPAD versions
are application schemas layered on top of GML 3.2.1; the shared GML mechanics
live in `pygeoapi_formatter_gml_npad.base`.

> **Status: scaffolding only.** GML serialization is not yet implemented.
> `write()` raises `NotImplementedError` until the NPAD schemas are wired in.

## Supported NPAD versions

| Version | Class              | Default `?f=` | Default media type                              |
| ------- | ------------------ | ------------- | ----------------------------------------------- |
| 4.5.2   | `NPAD452Formatter` | `gml`         | `application/gml+xml; profile="npad/4.5.2"`     |

NPAD 5.0 will be added later as a sibling subpackage.

`extension` is always `gml`. `attachment` is `True` (clients receive the
response with `Content-Disposition: attachment`).

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

Collections that expose only one NPAD version register the formatter with
defaults; clients request `?f=gml`:

```yaml
resources:
  my_plan_collection:
    type: collection
    providers:
      - type: feature
        name: postgresql_ext.PostgreSQLExtendedProvider
        # ...
    formatters:
      - name: pygeoapi_formatter_gml_npad.npad_4_5_2.NPAD452Formatter
```

```
GET /collections/my_plan_collection/items?f=gml
```

### Multi-version collection (overrides)

When a collection serves multiple NPAD versions simultaneously (transition
windows for kommuner), register one formatter instance per version. The
canonical version keeps the default `f='gml'`; non-canonical versions
override `f` and `mimetype` to avoid collision:

```yaml
formatters:
  - name: pygeoapi_formatter_gml_npad.npad_4_5_2.NPAD452Formatter
    # defaults: f='gml' (canonical for this collection)
  - name: pygeoapi_formatter_gml_npad.npad_5_0.NPAD50Formatter
    f: gml-npad-5
    mimetype: 'application/gml+xml; profile="npad/5.0"'
```

```
GET /collections/my_plan_collection/items?f=gml          # canonical (4.5.2)
GET /collections/my_plan_collection/items?f=gml-npad-5   # NPAD 5.0
```

The NPAD version is self-described in the response payload via `xmlns` and
`xsi:schemaLocation` regardless of which `?f=` value the client used.

### A note on `Accept`-header negotiation

`Accept`-header content negotiation cannot reliably discriminate between
NPAD versions on a collection that registers both. pygeoapi's format
dispatch matches on the media type but does not consider media type
parameters (e.g. `profile="npad/4.5.2"` vs `profile="npad/5.0"`). Use
`?f=` for deterministic version selection.

## License

MIT — see [LICENSE](LICENSE).
