"""Feature type configurations for Kommuneplan (20190401).

Covers kommuneplaner, kommuneplanforslag, kommunedelplaner and
kommunedelplanforslag databases.

Element order matches the XSD ``xs:sequence`` exactly, combining elements
from the base type hierarchy and the concrete type's extension.
Source: ``kommuneplan_20190401_filprod.xsd``.

Originally extracted from
``gml-export/src/gml_export/config/kommuneplan.py``.
"""

from ..mapping import (
    HOYDEFRAPLANBESTEMMELSE,
    IDENTIFIKASJON,
    KP_AREALPLAN_ID,
    KP_DELOMRADE_PREFIX,
    KP_KOPIDATA,
    KP_LINJER_OG_PUNKT_PREFIX,
    KP_PLANOMRADE_PREFIX,
    KVALITET,
    UTNYTTING,
    FeatureTypeConfig,
)

# --- KpOmråde extends Fellesegenskaper_PlanområdeType (unique base type) ---

KPOMRADE = FeatureTypeConfig(
    view_name="kpomrade_mv",
    feature_type_name="KpOmråde",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpomrade",
    element_order=KP_PLANOMRADE_PREFIX
    + [
        "område",
        "arealplanId",
        "plantype",
        "planstatus",
        "planbestemmelse",
        "lovreferanse",
        "lovreferanseBeskrivelse",
        "ikrafttredelsesdato",
        "plannavn",
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
        "lovreferanse": "lovreferanse",
        "lovreferanseBeskrivelse": "lovreferanseBeskrivelse",
        "ikrafttredelsesdato": "ikrafttredelsesdato",
        "vedtakEndeligPlanDato": "vedtakEndeligPlanDato",
        "kunngjøringsdato": "kunngjøringsdato",
        "opprinneligplanid": "opprinneligplanid",
        "opprinneligadministrativenhet": "opprinneligadministrativenhet",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
        "prosesshistorie": "prosesshistorie",
        "informasjon": "informasjon",
        "link": "link",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

# --- Area types extending DelområdeType ---

KPAREALFORMALOMRADE = FeatureTypeConfig(
    view_name="kparealformalomrade_mv",
    feature_type_name="KpArealformålOmråde",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kparealformalomrade",
    element_order=KP_DELOMRADE_PREFIX
    + [
        "område",
        "arealformål",
        "arealbruksstatus",
        "beskrivelse",
        "områdenavn",
        "utnytting",
        "uteoppholdsareal",
        "eierform",
    ],
    simple_properties={
        "arealformål": "arealformål",
        "arealbruksstatus": "arealbruksstatus",
        "beskrivelse": "beskrivelse",
        "områdenavn": "områdenavn",
        "uteoppholdsareal": "uteoppholdsareal",
        "eierform": "eierform",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA, UTNYTTING],
)

KPAREALBRUKOMRADE = FeatureTypeConfig(
    view_name="kparealbrukomrade_mv",
    feature_type_name="KpArealbrukOmråde",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kparealbrukomrade",
    element_order=KP_DELOMRADE_PREFIX
    + [
        "område",
        "arealbruk",
        "arealbruksstatus",
        "arealbruksutdyping",
        "områdenavn",
        "utnytting",
        "uteoppholdsareal",
    ],
    simple_properties={
        "arealbruk": "arealbruk",
        "arealbruksstatus": "arealbruksstatus",
        "arealbruksutdyping": "arealbruksutdyping",
        "områdenavn": "områdenavn",
        "uteoppholdsareal": "uteoppholdsareal",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA, UTNYTTING],
)

KPANGITTHENSYNSONE = FeatureTypeConfig(
    view_name="kpangitthensynsone_mv",
    feature_type_name="KpAngittHensynSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpangitthensynsone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPBANDLEGGINGSONE = FeatureTypeConfig(
    view_name="kpbandleggingsone_mv",
    feature_type_name="KpBåndleggingSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpbandleggingsone",
    element_order=KP_DELOMRADE_PREFIX
    + [
        "område",
        "båndlegging",
        "arealbruksstatus",
        "hensynSonenavn",
        "beskrivelse",
        "båndlagtFremTil",
    ],
    simple_properties={
        "båndlegging": "båndlegging",
        "arealbruksstatus": "arealbruksstatus",
        "hensynSonenavn": "hensynSonenavn",
        "beskrivelse": "beskrivelse",
        "båndlagtFremTil": "båndlagtFremTil",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPBESTEMMELSEOMRADE = FeatureTypeConfig(
    view_name="kpbestemmelseomrade_mv",
    feature_type_name="KpBestemmelseOmråde",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpbestemmelseomrade",
    element_order=KP_DELOMRADE_PREFIX
    + [
        "område",
        "bestemmelseOmrådeNavn",
        "type",
    ],
    simple_properties={
        "bestemmelseOmrådeNavn": "bestemmelseOmrådeNavn",
        "type": "type",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    default_values={"type": "other: ukjent"},
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPDETALJERINGSONE = FeatureTypeConfig(
    view_name="kpdetaljeringsone_mv",
    feature_type_name="KpDetaljeringSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpdetaljeringsone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPFARESONE = FeatureTypeConfig(
    view_name="kpfaresone_mv",
    feature_type_name="KpFareSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpfaresone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPGJENNOMFORINGSONE = FeatureTypeConfig(
    view_name="kpgjennomforingsone_mv",
    feature_type_name="KpGjennomføringSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpgjennomforingsone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPINFRASTRUKTURSONE = FeatureTypeConfig(
    view_name="kpinfrastruktursone_mv",
    feature_type_name="KpInfrastrukturSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpinfrastruktursone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

# --- Line/point types extending LinjerOgPunktType ---

KPINFRASTRUKTURLINJE = FeatureTypeConfig(
    view_name="kpinfrastrukturlinje_mv",
    feature_type_name="KpInfrastrukturLinje",
    geometry_column="geometri",
    geometry_gml_name="senterlinje",
    id_prefix="kpinfrastrukturlinje",
    element_order=KP_LINJER_OG_PUNKT_PREFIX
    + [
        "senterlinje",
        "infrastruktur",
        "vertikalnivå",
        "arealbruksstatus",
    ],
    simple_properties={
        "infrastruktur": "infrastruktur",
        "arealbruksstatus": "arealbruksstatus",
        "vertikalnivå": "vertikalnivå",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KP_KOPIDATA],
)

KPJURIDISKLINJE = FeatureTypeConfig(
    view_name="kpjuridisklinje_mv",
    feature_type_name="KpJuridiskLinje",
    geometry_column="geometri",
    geometry_gml_name="senterlinje",
    id_prefix="kpjuridisklinje",
    element_order=KP_LINJER_OG_PUNKT_PREFIX
    + [
        "senterlinje",
        "juridisklinje",
    ],
    simple_properties={
        "juridisklinje": "juridisklinje",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KP_KOPIDATA],
)

KPPASKRIFT = FeatureTypeConfig(
    view_name="kppaskrift_tekstplassering_mv",
    feature_type_name="KpPåskrift",
    geometry_column="geometri",
    geometry_gml_name="tekstplassering",
    id_prefix="kppaskrift",
    derived_point_geometry="objektposisjon",
    element_order=KP_LINJER_OG_PUNKT_PREFIX
    + [
        "objektposisjon",
        "tekstplassering",
        "generellTekststreng",
        "påskriftType",
    ],
    simple_properties={
        "generellTekststreng": "generellTekststreng",
        "påskriftType": "påskriftType",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KP_KOPIDATA],
)

KPREGULERTHOYDE = FeatureTypeConfig(
    view_name="kpregulerthoyde_mv",
    feature_type_name="KpRegulertHøyde",
    geometry_column="geometri",
    geometry_gml_name="senterlinje",
    id_prefix="kpregulerthoyde",
    element_order=KP_LINJER_OG_PUNKT_PREFIX
    + [
        "senterlinje",
        "høydefraplanbestemmelse",
    ],
    simple_properties={
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[
        KP_AREALPLAN_ID,
        IDENTIFIKASJON,
        KVALITET,
        KP_KOPIDATA,
        HOYDEFRAPLANBESTEMMELSE,
    ],
)

KPRESTRIKSJONOMRADE = FeatureTypeConfig(
    view_name="kprestriksjonomrade_mv",
    feature_type_name="KpRestriksjonOmråde",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kprestriksjonomrade",
    element_order=KP_DELOMRADE_PREFIX
    + [
        "område",
        "arealbruksstatus",
        "arealbruksrestriksjoner",
    ],
    simple_properties={
        "arealbruksstatus": "arealbruksstatus",
        "arealbruksrestriksjoner": "arealbruksrestriksjoner",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPRETNINGSLINJEOMRADE = FeatureTypeConfig(
    view_name="kpretningslinjeomrade_mv",
    feature_type_name="KpRetningslinjeOmråde",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpretningslinjeomrade",
    element_order=KP_DELOMRADE_PREFIX
    + [
        "område",
        "arealbruksretningslinjer",
    ],
    simple_properties={
        "arealbruksretningslinjer": "arealbruksretningslinjer",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPSAMFERDSELLINJE = FeatureTypeConfig(
    view_name="kpsamferdsellinje_mv",
    feature_type_name="KpSamferdselLinje",
    geometry_column="geometri",
    geometry_gml_name="grense",
    id_prefix="kpsamferdsellinje",
    element_order=KP_LINJER_OG_PUNKT_PREFIX
    + [
        "grense",
        "samferdselslinje",
        "vertikalnivå",
        "arealbruksstatus",
        "viktighet",
        "holdningsklasse",
    ],
    simple_properties={
        "samferdselslinje": "samferdselslinje",
        "arealbruksstatus": "arealbruksstatus",
        "vertikalnivå": "vertikalnivå",
        "viktighet": "viktighet",
        "holdningsklasse": "holdningsklasse",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KP_KOPIDATA],
)

KPSAMFERDSELPUNKT = FeatureTypeConfig(
    view_name="kpsamferdselpunkt_mv",
    feature_type_name="KpSamferdselPunkt",
    geometry_column="geometri",
    geometry_gml_name="posisjon",
    id_prefix="kpsamferdselpunkt",
    element_order=KP_LINJER_OG_PUNKT_PREFIX
    + [
        "posisjon",
        "samferdselspunkt",
        "vertikalnivå",
        "arealbruksstatus",
        "viktighet",
    ],
    simple_properties={
        "samferdselspunkt": "samferdselspunkt",
        "arealbruksstatus": "arealbruksstatus",
        "vertikalnivå": "vertikalnivå",
        "viktighet": "viktighet",
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KVALITET, KP_KOPIDATA],
)

# --- Hensynssone types extending DelområdeType ---

KPSIKRINGSONE = FeatureTypeConfig(
    view_name="kpsikringsone_mv",
    feature_type_name="KpSikringSone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpsikringsone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)

KPSTOYSONE = FeatureTypeConfig(
    view_name="kpstoysone_mv",
    feature_type_name="KpStøySone",
    geometry_column="geometri",
    geometry_gml_name="område",
    id_prefix="kpstoysone",
    element_order=KP_DELOMRADE_PREFIX
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
        "førsteDigitaliseringsdato": "førsteDigitaliseringsdato",
        "oppdateringsdato": "oppdateringsdato",
    },
    nested_groups=[KP_AREALPLAN_ID, IDENTIFIKASJON, KP_KOPIDATA],
)


ALL_KP_FEATURE_TYPES: list[FeatureTypeConfig] = [
    KPOMRADE,
    KPAREALFORMALOMRADE,
    KPAREALBRUKOMRADE,
    KPANGITTHENSYNSONE,
    KPBANDLEGGINGSONE,
    KPBESTEMMELSEOMRADE,
    KPDETALJERINGSONE,
    KPFARESONE,
    KPGJENNOMFORINGSONE,
    KPINFRASTRUKTURLINJE,
    KPINFRASTRUKTURSONE,
    KPJURIDISKLINJE,
    KPPASKRIFT,
    KPREGULERTHOYDE,
    KPRESTRIKSJONOMRADE,
    KPRETNINGSLINJEOMRADE,
    KPSAMFERDSELLINJE,
    KPSAMFERDSELPUNKT,
    KPSIKRINGSONE,
    KPSTOYSONE,
]

FEATURE_TYPES: dict[str, FeatureTypeConfig] = {
    fc.feature_type_name: fc for fc in ALL_KP_FEATURE_TYPES
}
"""Lookup table keyed by SOSI ``feature_type_name`` (e.g. ``"KpOmråde"``)."""

FEATURE_TYPES_BY_VIEW: dict[str, FeatureTypeConfig] = {
    fc.view_name: fc for fc in ALL_KP_FEATURE_TYPES
}
"""Lookup table keyed by materialized view name (e.g. ``"kpomrade_mv"``).

Provided as a convenience for consumers like ``gml-export`` that dispatch
by view name rather than feature type name.
"""
