"""Feature type configurations for Reguleringsplan (20190401).

Covers reguleringsplaner and reguleringsplanforslag databases. View names
and properties derived from materialized-view column mappings; DB column
names use the translated forms (e.g. ``førsteDigitaliseringsdato``, not
``forstedigitaliseringsdato``).

Element order matches the XSD ``xs:sequence`` exactly, combining elements
from the base type hierarchy and the concrete type's extension.

Originally extracted from
``gml-export/src/gml_export/config/reguleringsplan.py``.
"""

from ..mapping import (
    DELOMRADE_PREFIX,
    HOYDEFRAPLANBESTEMMELSE,
    IDENTIFIKASJON,
    KOPIDATA,
    KVALITET,
    LINJER_OG_PUNKT_PREFIX,
    PLANOMRADE_PREFIX,
    RB_AREALPLAN_ID,
    RP_AREALPLAN_ID,
    RP_UTNYTTING,
    SAKSNUMMER,
    UTNYTTING,
    FeatureTypeConfig,
    SchemaInfo,
)

SCHEMA_INFO = SchemaInfo(
    namespace=(
        "http://skjema.geonorge.no/SOSI/produktspesifikasjon/Reguleringsplan/20190401"
    ),
    schema_location=(
        "https://skjema.geonorge.no/SOSI/produktspesifikasjon/"
        "Reguleringsplan/20190401/reguleringsplan_20190401_filprod.xsd"
    ),
    prefix="app",
)
"""SOSI GML schema metadata for Reguleringsplan (20190401).

The formatter's class-level ``SCHEMA_NAMESPACE`` / ``SCHEMA_LOCATION`` /
``SCHEMA_PREFIX`` are derived from this. Re-exported from the subpackage
``__init__`` so external consumers (e.g. ``gml-export``) can import it
without depending on the formatter class.
"""

# --- Reguleringsplan (Rp*) feature types ---

# RpOmråde extends Fellesegenskaper_PlanområdeType (unique base type)
RPOMRADE = FeatureTypeConfig(
    view_name="rpomrade_omrade_mv",
    feature_type_name="RpOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpomrade",
    element_order=PLANOMRADE_PREFIX
    + [
        "område",
        "arealplanId",
        "vertikalnivå",
        "plantype",
        "planstatus",
        "plannavn",
        "planbestemmelse",
        "ikrafttredelsesdato",
        "lovreferanse",
        "lovreferanseBeskrivelse",
        "forslagsstillerType",
        "vedtakEndeligPlanDato",
        "kunngjøringsdato",
        "opprinneligplanid",
        "opprinneligadministrativenhet",
    ],
    simple_properties={
        "plantype": "plantype",
        "planstatus": "planstatus",
        "plannavn": "plannavn",
        "planbestemmelse": "planbestemmelse",
        "ikrafttredelsesdato": "ikrafttredelsesdato",
        "lovreferanse": "lovreferanse",
        "lovreferanseBeskrivelse": "lovreferanseBeskrivelse",
        "forslagsstillerType": "forslagsstillerType",
        "vedtakEndeligPlanDato": "vedtakEndeligPlanDato",
        "kunngjøringsdato": "kunngjøringsdato",
        "opprinneligplanid": "opprinneligplanid",
        "opprinneligadministrativenhet": "opprinneligadministrativenhet",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
        "prosesshistorie": "prosesshistorie",
        "informasjon": "informasjon",
        "link": "link",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

# --- Delområde-based types (extends DelområdeType) ---
# Base element order: identifikasjon, førsteDigitaliseringsdato, oppdateringsdato,
# kopidata, arealplanId, vertikalnivå, then type-specific extension elements.

RPAREALFORMALOMRADE = FeatureTypeConfig(
    view_name="rparealformalomrade_omrade_mv",
    feature_type_name="RpArealformålOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rparealformalomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "eierform",
        "arealformål",
        "beskrivelse",
        "feltbetegnelse",
        "utnytting",
        "uteoppholdsareal",
        "byggverkbestemmelse",
        "avkjørselsbestemmelse",
    ],
    simple_properties={
        "eierform": "eierform",
        "arealformål": "arealformål",
        "beskrivelse": "beskrivelse",
        "feltbetegnelse": "feltbetegnelse",
        "uteoppholdsareal": "uteoppholdsareal",
        "byggverkbestemmelse": "byggverkbestemmelse",
        "avkjørselsbestemmelse": "avkjørselsbestemmelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA, RP_UTNYTTING],
)

RPANGITTHENSYNSONE = FeatureTypeConfig(
    view_name="rpangitthensynsone_omrade_mv",
    feature_type_name="RpAngittHensynSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpangitthensynsone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "angittHensyn",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "angittHensyn": "angittHensyn",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPBANDLEGGINGSONE = FeatureTypeConfig(
    view_name="rpbandleggingsone_omrade_mv",
    feature_type_name="RpBåndleggingSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpbandleggingsone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "båndlegging",
        "båndlagtFremTil",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "båndlegging": "båndlegging",
        "båndlagtFremTil": "båndlagtFremTil",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPBESTEMMELSEOMRADE = FeatureTypeConfig(
    view_name="rpbestemmelseomrade_omrade_mv",
    feature_type_name="RpBestemmelseOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpbestemmelseomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "bestemmelseOmrådeNavn",
        "type",
    ],
    simple_properties={
        "bestemmelseOmrådeNavn": "bestemmelseOmrådeNavn",
        "type": "type",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    default_values={"type": "other: ukjent"},
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPDETALJERINGSONE = FeatureTypeConfig(
    view_name="rpdetaljeringsone_omrade_mv",
    feature_type_name="RpDetaljeringSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpdetaljeringsone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "detaljering",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "detaljering": "detaljering",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPFARESONE = FeatureTypeConfig(
    view_name="rpfaresone_omrade_mv",
    feature_type_name="RpFareSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpfaresone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "fare",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "fare": "fare",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPGJENNOMFORINGSONE = FeatureTypeConfig(
    view_name="rpgjennomforingsone_omrade_mv",
    feature_type_name="RpGjennomføringSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpgjennomforingsone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "gjennomføring",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "gjennomføring": "gjennomføring",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPINFRASTRUKTURSONE = FeatureTypeConfig(
    view_name="rpinfrastruktursone_omrade_mv",
    feature_type_name="RpInfrastrukturSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpinfrastruktursone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "infrastruktur",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "infrastruktur": "infrastruktur",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPSIKRINGSONE = FeatureTypeConfig(
    view_name="rpsikringsone_omrade_mv",
    feature_type_name="RpSikringSone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpsikringsone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "sikring",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "sikring": "sikring",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RPSTOYSONE = FeatureTypeConfig(
    view_name="rpstoysone_omrade_mv",
    feature_type_name="RpStøySone",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rpstoysone",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "støy",
        "hensynSonenavn",
        "beskrivelse",
    ],
    simple_properties={
        "støy": "støy",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

# --- LinjerOgPunkt-based types (extends LinjerOgPunktType) ---
# Base element order: identifikasjon, førsteDigitaliseringsdato, oppdateringsdato,
# kvalitet, kopidata, arealplanId, vertikalnivå, then type-specific elements.

RPJURIDISKLINJE = FeatureTypeConfig(
    view_name="rpjuridisklinje_senterlinje_mv",
    feature_type_name="RpJuridiskLinje",
    geometry_column="senterlinje",
    geometry_gml_name="senterlinje",
    id_prefix="rpjuridisklinje",
    element_order=LINJER_OG_PUNKT_PREFIX
    + [
        "senterlinje",
        "juridisklinje",
    ],
    simple_properties={
        "juridisklinje": "juridisklinje",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KOPIDATA],
)

# Note: XSD defines symbolretning (gml:VectorType, optional) between
# objektposisjon and juridiskpunkt. The MV has symbolretning as a computed
# sin/cos vector but it requires special GML handling (not a simple text
# value). Omitted for now; rotasjon is not an XSD element so also excluded.
RPJURIDISKPUNKT = FeatureTypeConfig(
    view_name="rpjuridiskpunkt_objektposisjon_mv",
    feature_type_name="RpJuridiskPunkt",
    geometry_column="objektposisjon",
    geometry_gml_name="objektposisjon",
    id_prefix="rpjuridiskpunkt",
    element_order=LINJER_OG_PUNKT_PREFIX
    + [
        "objektposisjon",
        "juridiskpunkt",
    ],
    simple_properties={
        "juridiskpunkt": "juridiskpunkt",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KOPIDATA],
)

# objektposisjon is derived from tekstplassering: start point for lines,
# passthrough for points. The DB query computes this via ST_PointN.
RPPASKRIFT = FeatureTypeConfig(
    view_name="rppaskrift_tekstplassering_mv",
    feature_type_name="RpPåskrift",
    geometry_column="tekstplassering",
    geometry_gml_name="tekstplassering",
    id_prefix="rppaskrift",
    derived_point_geometry="objektposisjon",
    element_order=LINJER_OG_PUNKT_PREFIX
    + [
        "objektposisjon",
        "tekstplassering",
        "generellTekststreng",
        "påskriftType",
    ],
    simple_properties={
        "generellTekststreng": "generellTekststreng",
        "påskriftType": "påskriftType",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KOPIDATA],
)

RPREGULERTHOYDE = FeatureTypeConfig(
    view_name="rpregulerthoyde_senterlinje_mv",
    feature_type_name="RpRegulertHøyde",
    geometry_column="senterlinje",
    geometry_gml_name="senterlinje",
    id_prefix="rpregulerthoyde",
    element_order=LINJER_OG_PUNKT_PREFIX
    + [
        "senterlinje",
        "høydefraplanbestemmelse",
    ],
    simple_properties={
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[
        RP_AREALPLAN_ID,
        IDENTIFIKASJON,
        KVALITET,
        KOPIDATA,
        HOYDEFRAPLANBESTEMMELSE,
    ],
)

# --- Reguleringsbestemmelse (Rb*) and Pbl* feature types ---
# All extend DelområdeType.

PBLMIDLBYGGANLEGGOMRADE = FeatureTypeConfig(
    view_name="pblmidlbygganleggomrade_omrade_mv",
    feature_type_name="PblMidlByggAnleggOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="pblmidlbygganleggomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "bestemmelseOmrådeNavn",
        "saksnummer",
        "avgjørelsesdato",
        "gyldigTilDato",
    ],
    simple_properties={
        "bestemmelseOmrådeNavn": "bestemmelseOmrådeNavn",
        "avgjørelsesdato": "avgjørelsesdato",
        "gyldigTilDato": "gyldigTilDato",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RP_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA, SAKSNUMMER],
)

RBBEVARINGOMRADE = FeatureTypeConfig(
    view_name="rbbevaringomrade_omrade_mv",
    feature_type_name="RbBevaringOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rbbevaringomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "reguleringsformål",
        "feltbetegnelse",
    ],
    simple_properties={
        "reguleringsformål": "reguleringsformål",
        "feltbetegnelse": "feltbetegnelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RB_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RBFAREOMRADE = FeatureTypeConfig(
    view_name="rbfareomrade_omrade_mv",
    feature_type_name="RbFareOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rbfareomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "reguleringsformål",
        "feltbetegnelse",
        "reguleringsformålsutdyping",
    ],
    simple_properties={
        "reguleringsformål": "reguleringsformål",
        "feltbetegnelse": "feltbetegnelse",
        "reguleringsformålsutdyping": "reguleringsformålsutdyping",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RB_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RBFORMALOMRADE = FeatureTypeConfig(
    view_name="rbformalomrade_omrade_mv",
    feature_type_name="RbFormålOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rbformalomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "reguleringsformål",
        "reguleringsformålsutdyping",
        "feltbetegnelse",
        "utnytting",
        "uteoppholdsareal",
        "byggverkbestemmelse",
        "avkjørselsbestemmelse",
    ],
    simple_properties={
        "reguleringsformål": "reguleringsformål",
        "reguleringsformålsutdyping": "reguleringsformålsutdyping",
        "feltbetegnelse": "feltbetegnelse",
        "uteoppholdsareal": "uteoppholdsareal",
        "byggverkbestemmelse": "byggverkbestemmelse",
        "avkjørselsbestemmelse": "avkjørselsbestemmelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RB_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA, UTNYTTING],
)

RBFORNYELSEOMRADE = FeatureTypeConfig(
    view_name="rbfornyelseomrade_omrade_mv",
    feature_type_name="RbFornyelseOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rbfornyelseomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "reguleringsformål",
        "feltbetegnelse",
    ],
    simple_properties={
        "reguleringsformål": "reguleringsformål",
        "feltbetegnelse": "feltbetegnelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RB_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RBREKKEFOLGEOMRADE = FeatureTypeConfig(
    view_name="rbrekkefolgeomrade_omrade_mv",
    feature_type_name="RbRekkefølgeOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rbrekkefolgeomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "reguleringsformål",
        "feltbetegnelse",
    ],
    simple_properties={
        "reguleringsformål": "reguleringsformål",
        "feltbetegnelse": "feltbetegnelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RB_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)

RBRESTRIKSJONOMRADE = FeatureTypeConfig(
    view_name="rbrestriksjonomrade_omrade_mv",
    feature_type_name="RbRestriksjonOmråde",
    geometry_column="område",
    geometry_gml_name="område",
    id_prefix="rbrestriksjonomrade",
    element_order=DELOMRADE_PREFIX
    + [
        "område",
        "reguleringsformål",
        "feltbetegnelse",
    ],
    simple_properties={
        "reguleringsformål": "reguleringsformål",
        "feltbetegnelse": "feltbetegnelse",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[RB_AREALPLAN_ID, IDENTIFIKASJON, KOPIDATA],
)


ALL_RP_FEATURE_TYPES: list[FeatureTypeConfig] = [
    RPOMRADE,
    RPAREALFORMALOMRADE,
    RPANGITTHENSYNSONE,
    RPBANDLEGGINGSONE,
    RPBESTEMMELSEOMRADE,
    RPDETALJERINGSONE,
    RPFARESONE,
    RPGJENNOMFORINGSONE,
    RPINFRASTRUKTURSONE,
    RPJURIDISKLINJE,
    RPJURIDISKPUNKT,
    RPPASKRIFT,
    RPREGULERTHOYDE,
    RPSIKRINGSONE,
    RPSTOYSONE,
    PBLMIDLBYGGANLEGGOMRADE,
    RBBEVARINGOMRADE,
    RBFAREOMRADE,
    RBFORMALOMRADE,
    RBFORNYELSEOMRADE,
    RBREKKEFOLGEOMRADE,
    RBRESTRIKSJONOMRADE,
]

FEATURE_TYPES: dict[str, FeatureTypeConfig] = {
    fc.feature_type_name: fc for fc in ALL_RP_FEATURE_TYPES
}
"""Lookup table keyed by SOSI ``feature_type_name`` (e.g. ``"RpOmråde"``)."""

FEATURE_TYPES_BY_VIEW: dict[str, FeatureTypeConfig] = {
    fc.view_name: fc for fc in ALL_RP_FEATURE_TYPES
}
"""Lookup table keyed by materialized view name (e.g. ``"rpomrade_omrade_mv"``).

Provided as a convenience for consumers like ``gml-export`` that dispatch
by view name rather than feature type name.
"""
