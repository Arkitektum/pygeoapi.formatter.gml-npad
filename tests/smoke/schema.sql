-- Minimal smoke-test schema for the SOSI GML formatter.
--
-- These are TABLEs (not MATERIALIZED VIEWs) for setup simplicity; postgresql_ext
-- treats them identically via SQLAlchemy reflection. The column set is the
-- minimum required to exercise the property-roundtrip path through
-- FeatureTypeConfig.nested_groups + simple_properties: the identifikasjon /
-- arealplanId / kopidata wrappers plus one or two simple properties.
--
-- Diacritics and dots in column names are required by the SOSI / NPAD convention
-- and must be double-quoted. The geom column name differs between RP (`område`)
-- and KP (`geometri`) — matches gml-export's FeatureTypeConfig.geometry_column.
--
-- `_geometry_gml` and `_derived_point_gml` columns are intentionally absent.
-- They land when postgresql_ext PR2 (`gml_passthrough`) and the corresponding
-- MV column additions ship. Until then, formatter responses are property-only
-- and run with `validate: false` since SOSI XSDs require geometry.

CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS rpomrade_omrade_mv CASCADE;
DROP TABLE IF EXISTS kpomrade_mv CASCADE;

-- Reguleringsplan: RpOmråde
CREATE TABLE rpomrade_omrade_mv (
    objid                              bigint PRIMARY KEY,
    "område"                           geometry(Polygon, 25833),
    "identifikasjon.lokalId"           text,
    "identifikasjon.navnerom"          text,
    "identifikasjon.versjonId"         text,
    "arealplanId.kommunenummer"        text,
    "arealplanId.landkode"             text,
    "arealplanId.planidentifikasjon"   text,
    "kopidata.områdeId"                text,
    "kopidata.originalDatavert"        text,
    "kopidata.kopidato"                date,
    plantype                           text,
    planstatus                         text,
    plannavn                           text
);

-- Kommuneplan: KpOmråde. Note `geometri` (not `område`) for the geom column —
-- matches the production MV column name in gml-export's FeatureTypeConfig.
CREATE TABLE kpomrade_mv (
    objid                              bigint PRIMARY KEY,
    "geometri"                         geometry(Polygon, 25833),
    "identifikasjon.lokalId"           text,
    "identifikasjon.navnerom"          text,
    "identifikasjon.versjonId"         text,
    "arealplanId.kommunenummer"        text,
    "arealplanId.landkode"             text,
    "arealplanId.planidentifikasjon"   text,
    "kopidata.områdeId"                text,
    "kopidata.originalDatavert"        text,
    "kopidata.kopidato"                date,
    plantype                           text,
    planstatus                         text,
    plannavn                           text
);
