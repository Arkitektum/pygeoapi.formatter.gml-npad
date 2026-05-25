-- Smoke-test fixtures: one row per table covering the minimum set of nested
-- groups + a couple of simple properties. Polygon geometries are placeholder
-- shapes near Oslo (kommunenummer 0301).

TRUNCATE TABLE rpomrade_omrade_mv, kpomrade_mv;

INSERT INTO rpomrade_omrade_mv (
    objid,
    "område",
    "identifikasjon.lokalId",
    "identifikasjon.navnerom",
    "identifikasjon.versjonId",
    "arealplanId.kommunenummer",
    "arealplanId.landkode",
    "arealplanId.planidentifikasjon",
    "kopidata.områdeId",
    "kopidata.originalDatavert",
    "kopidata.kopidato",
    plantype,
    planstatus,
    plannavn
) VALUES (
    1,
    ST_GeomFromText('POLYGON((597000 6643000, 598000 6643000, 598000 6644000, 597000 6644000, 597000 6643000))', 25833),
    'rp-smoke-001',
    'https://data.geonorge.no/SOSI/produktspesifikasjon/Reguleringsplan/20190401',
    '1',
    '301',
    'NO',
    'rp-plan-0001',
    '0301-test-omrade-01',
    'Kartverket',
    '2019-04-01',
    '35',
    '4',
    'Smoke Test Reguleringsplan'
);

INSERT INTO kpomrade_mv (
    objid,
    "geometri",
    "identifikasjon.lokalId",
    "identifikasjon.navnerom",
    "identifikasjon.versjonId",
    "arealplanId.kommunenummer",
    "arealplanId.landkode",
    "arealplanId.planidentifikasjon",
    "kopidata.områdeId",
    "kopidata.originalDatavert",
    "kopidata.kopidato",
    plantype,
    planstatus,
    plannavn
) VALUES (
    1,
    ST_GeomFromText('POLYGON((598000 6644000, 599000 6644000, 599000 6645000, 598000 6645000, 598000 6644000))', 25833),
    'kp-smoke-001',
    'https://data.geonorge.no/SOSI/produktspesifikasjon/Kommuneplan/20190401',
    '1',
    '301',
    'NO',
    'kp-plan-0001',
    '0301-test-kpomrade-01',
    'Kartverket',
    '2019-04-01',
    '20',
    '4',
    'Smoke Test Kommuneplan'
);
