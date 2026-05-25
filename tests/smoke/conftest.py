"""Smoke-test fixtures.

Connection params come from env vars so the same tests run locally (against
a developer's docker-postgres) and in CI (against the workflow's postgres
service). Defaults match the GitHub Actions job in
``.github/workflows/smoke.yml``.

The session-scoped ``smoke_db`` autouse fixture loads ``schema.sql`` and
``fixtures.sql`` once per pytest invocation. Tests run against the loaded
state; teardown is implicit (each test invocation rebuilds the schema).
"""

import os
import pathlib

import pytest

# Skip the entire smoke directory if smoke deps aren't installed. Default
# `pytest` invocations (without `-m smoke`) still trip over conftest imports
# during collection; importorskip short-circuits that cleanly.
#
# Run with `pip install -e '.[smoke]'` for the Python-side deps.
#
# `postgresql_ext` additionally imports `osgeo` (GDAL Python bindings) at
# module top — `pip install gdal` is not enough; the system needs libgdal
# installed first (`apt-get install libgdal-dev gdal-bin` on Ubuntu/WSL,
# then `pip install gdal==$(gdal-config --version)`). The CI workflow does
# this automatically; locally it's a developer prerequisite. When GDAL is
# missing, the importorskip below skips the smoke directory cleanly.
psycopg = pytest.importorskip(
    "psycopg", reason="smoke tests require psycopg (pip install -e '.[smoke]')"
)
pytest.importorskip(
    "postgresql_ext",
    reason=(
        "smoke tests require postgresql_ext + GDAL "
        "(see tests/smoke/conftest.py header for install commands)"
    ),
)

_HERE = pathlib.Path(__file__).parent


def _conn_str() -> str:
    return (
        f"host={os.environ.get('SMOKE_DB_HOST', 'localhost')} "
        f"port={os.environ.get('SMOKE_DB_PORT', '5432')} "
        f"dbname={os.environ.get('SMOKE_DB_NAME', 'smoke')} "
        f"user={os.environ.get('SMOKE_DB_USER', 'smoke')} "
        f"password={os.environ.get('SMOKE_DB_PASSWORD', 'smoke')}"
    )


@pytest.fixture(scope="session", autouse=True)
def smoke_db():
    """Load schema + fixtures into the smoke postgres once per test session."""
    schema_sql = (_HERE / "schema.sql").read_text(encoding="utf-8")
    fixtures_sql = (_HERE / "fixtures.sql").read_text(encoding="utf-8")

    with psycopg.connect(_conn_str(), autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(schema_sql)
        cur.execute(fixtures_sql)

    yield


def _provider_def(table: str, geom_field: str) -> dict:
    return {
        "type": "feature",
        "name": "postgresql_ext.PostgreSQLExtendedProvider",
        # property_shape: dotted is the contract this formatter requires.
        # Available in postgresql_ext v0.3.0+. Until that ships, this smoke
        # job will fail at provider init — that's the intended signal.
        "property_shape": "dotted",
        "data": {
            "host": os.environ.get("SMOKE_DB_HOST", "localhost"),
            "port": int(os.environ.get("SMOKE_DB_PORT", "5432")),
            "dbname": os.environ.get("SMOKE_DB_NAME", "smoke"),
            "user": os.environ.get("SMOKE_DB_USER", "smoke"),
            "password": os.environ.get("SMOKE_DB_PASSWORD", "smoke"),
            "search_path": ["public"],
        },
        "id_field": "objid",
        "table": table,
        "geom_field": geom_field,
    }


@pytest.fixture(scope="session")
def rp_provider_def() -> dict:
    return _provider_def("rpomrade_omrade_mv", "område")


@pytest.fixture(scope="session")
def kp_provider_def() -> dict:
    return _provider_def("kpomrade_mv", "geometri")
