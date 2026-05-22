"""SOSI GML data-mapping types and shared element-group constants.

Defines the dataclasses (:class:`SchemaInfo`, :class:`NestedGroup`,
:class:`FeatureTypeConfig`) and the reusable :class:`NestedGroup` constants
used by both Reguleringsplan and Kommuneplan feature-type configurations.

The mapping model assumes flat dot-separated database column names
(e.g. ``identifikasjon.lokalId``) that are reconstructed into nested GML
elements during serialization. This matches the materialized views in
pygeoapi.plandata's PostgreSQL layer.

Originally extracted from ``gml-export/src/gml_export/feature_mapping.py``
and ``schema_registry.py`` in the DiBK.Oppsamlingsregister repo. See ADR /
PR description for the dependency-inversion rationale.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SchemaInfo:
    """SOSI GML schema metadata for a (product spec, version) pair."""

    namespace: str
    """Application namespace, e.g.
    ``http://skjema.geonorge.no/SOSI/produktspesifikasjon/Reguleringsplan/20190401``
    """

    schema_location: str
    """Full URL to the XSD file."""

    prefix: str
    """XML namespace prefix to use, e.g. ``app``."""


@dataclass(frozen=True)
class NestedGroup:
    """Defines how flat DB columns map to a nested GML element group.

    Example: ``identifikasjon.lokalId``, ``identifikasjon.navnerom`` →

        <identifikasjon>
          <Identifikasjon>
            <lokalId>value</lokalId>
            <navnerom>value</navnerom>
          </Identifikasjon>
        </identifikasjon>
    """

    gml_parent: str
    """Outer element name, e.g. ``identifikasjon``."""

    gml_wrapper_type: str
    """Inner wrapper element name (the type), e.g. ``Identifikasjon``."""

    columns: dict[str, str]
    """Mapping of DB column name → GML child element name.
    e.g. ``{"identifikasjon.lokalId": "lokalId"}``.
    """

    repeating: bool = False
    """If True, column values are parallel arrays (from PostgreSQL array
    columns) and each index produces a separate outer/wrapper group
    instance. Used for XSD elements with ``maxOccurs="unbounded"``.
    """

    zero_pad_columns: dict[str, int] = field(default_factory=dict)
    """DB column names that need zero-padding to a fixed width.
    Maps column name → target width. e.g. ``{"arealplanId.kommunenummer": 4}``.
    """

    date_only_columns: frozenset[str] = frozenset()
    """DB column names whose values should be formatted as date-only
    (``YYYY-MM-DD``), even if the DB returns a full timestamp. Used for
    XSD ``xs:date`` fields.
    """

    force_datetime_columns: frozenset[str] = frozenset()
    """DB column names whose date values should be formatted as
    ``xs:dateTime``, even if the DB returns a date-only value. Appends
    ``T00:00:00`` to dates.
    """

    required_columns: frozenset[str] = frozenset()
    """DB column names that are required by the XSD. If any required
    column is null, the entire nested group is skipped (to avoid writing
    a wrapper with missing mandatory children).
    """

    default_values: dict[str, str] = field(default_factory=dict)
    """Fallback values for DB columns that are always null in the source
    data but required by the XSD. Applied when the column value is None.
    """


@dataclass(frozen=True)
class FeatureTypeConfig:
    """Complete mapping for one materialized view → one SOSI GML feature type."""

    view_name: str
    """Materialized view name, e.g. ``rpomrade_omrade_mv``."""

    feature_type_name: str
    """SOSI GML feature type name, e.g. ``RpOmråde``."""

    geometry_column: str
    """DB column containing the geometry, e.g. ``område``."""

    geometry_gml_name: str
    """GML element name for the geometry, e.g. ``område``."""

    element_order: list[str] = field(default_factory=list)
    """XSD-conformant element output order. Each entry is a GML element
    name that maps to either: the geometry (matches ``geometry_gml_name``),
    a nested group (matches ``NestedGroup.gml_parent``), or a simple
    property (matches the value in ``simple_properties``). XSD
    ``xs:sequence`` requires strict ordering.
    """

    simple_properties: dict[str, str] = field(default_factory=dict)
    """Flat DB column → GML element name for non-nested properties.
    e.g. ``{"plantype": "plantype", "planstatus": "planstatus"}``.
    """

    nested_groups: list[NestedGroup] = field(default_factory=list)
    """Nested element groups (``identifikasjon``, ``arealplanId``,
    ``kopidata``, etc.).
    """

    id_prefix: str = ""
    """Prefix for ``gml:id`` attribute, e.g. ``rpomrade``."""

    derived_point_geometry: str = ""
    """GML element name for a point geometry derived from the primary
    geometry. For lines, extracts the start point; for points, passes
    through unchanged. Used when the XSD requires a separate point element
    alongside the primary geometry (e.g. ``objektposisjon`` in
    ``RpPåskrift``).
    """

    default_values: dict[str, str] = field(default_factory=dict)
    """Fallback values for simple-property DB columns that are always null
    in the source data but required by the XSD. Keyed by DB column name
    (matching the keys in ``simple_properties``). Applied when the column
    value is None.
    """


# ---------------------------------------------------------------------------
# Shared NestedGroup definitions reused across feature types
# ---------------------------------------------------------------------------

IDENTIFIKASJON = NestedGroup(
    gml_parent="identifikasjon",
    gml_wrapper_type="Identifikasjon",
    columns={
        "identifikasjon.lokalId": "lokalId",
        "identifikasjon.navnerom": "navnerom",
        "identifikasjon.versjonId": "versjonId",
    },
)

RP_AREALPLAN_ID = NestedGroup(
    gml_parent="arealplanId",
    gml_wrapper_type="NasjonalArealplanId",
    columns={
        "arealplanId.kommunenummer": "kommunenummer",
        "arealplanId.landkode": "landkode",
        "arealplanId.planidentifikasjon": "planidentifikasjon",
    },
    zero_pad_columns={"arealplanId.kommunenummer": 4},
)

# KP and RB reuse RP's arealplanId structure verbatim at version 20190401.
KP_AREALPLAN_ID = RP_AREALPLAN_ID
RB_AREALPLAN_ID = RP_AREALPLAN_ID

KOPIDATA = NestedGroup(
    gml_parent="kopidata",
    gml_wrapper_type="Kopidata",
    columns={
        "kopidata.områdeId": "områdeId",
        "kopidata.originalDatavert": "originalDatavert",
        "kopidata.kopidato": "kopidato",
    },
    date_only_columns=frozenset({"kopidata.kopidato"}),
)

# KP XSD defines kopidato as xs:dateTime (not xs:date like RP).
# The DB returns a date value; force_datetime_columns upgrades it.
KP_KOPIDATA = NestedGroup(
    gml_parent="kopidata",
    gml_wrapper_type="Kopidata",
    columns={
        "kopidata.områdeId": "områdeId",
        "kopidata.originalDatavert": "originalDatavert",
        "kopidata.kopidato": "kopidato",
    },
    force_datetime_columns=frozenset({"kopidata.kopidato"}),
)

KVALITET = NestedGroup(
    gml_parent="kvalitet",
    gml_wrapper_type="Posisjonskvalitet",
    columns={
        "kvalitet.målemetode": "målemetode",
        "kvalitet.nøyaktighet": "nøyaktighet",
    },
)

SAKSNUMMER = NestedGroup(
    gml_parent="saksnummer",
    gml_wrapper_type="Saksnummer",
    columns={
        "saksnummer.saksår": "saksår",
        "saksnummer.sakssekvensnummer": "sakssekvensnummer",
    },
)

UTNYTTING = NestedGroup(
    gml_parent="utnytting",
    gml_wrapper_type="Utnytting",
    repeating=True,
    columns={
        "utnytting.utnyttingstype": "utnyttingstype",
        "utnytting.utnyttingstall": "utnyttingstall",
        "utnytting.utnyttingstall_minimum": "utnyttingstall_minimum",
    },
)

# Rp* types use RpUtnytting (different XSD wrapper from Rb's Utnytting).
RP_UTNYTTING = NestedGroup(
    gml_parent="utnytting",
    gml_wrapper_type="RpUtnytting",
    repeating=True,
    columns={
        "utnytting.utnyttingstype": "utnyttingstype",
        "utnytting.utnyttingstall": "utnyttingstall",
        "utnytting.utnyttingstall_minimum": "utnyttingstall_minimum",
    },
)

HOYDEFRAPLANBESTEMMELSE = NestedGroup(
    gml_parent="høydefraplanbestemmelse",
    gml_wrapper_type="HøydeFraPlanbestemmelse",
    columns={
        "høydefraplanbestemmelse.regulerthøyde": "regulerthøyde",
        "høydefraplanbestemmelse.høydereferansesystem": "høydereferansesystem",
    },
    default_values={
        "høydefraplanbestemmelse.høydereferansesystem": "other: ukjent",
    },
)


# ---------------------------------------------------------------------------
# Element-order prefixes (from XSD base types)
# ---------------------------------------------------------------------------
# These define the element order inherited from the abstract base types.
# Each concrete feature type appends its own elements after these.
#
# IMPORTANT: The RP and KP XSDs define different element orders for the same
# conceptual base types. Use RP_* prefixes for reguleringsplan and KP_* for
# kommuneplan feature types.

# Reguleringsplan (RP) prefixes — from reguleringsplan_20190401_filprod.xsd

# Fellesegenskaper_PlanområdeType (used by RpOmråde)
PLANOMRADE_PREFIX: list[str] = [
    "identifikasjon",
    "førsteDigitaliseringsdato",
    "prosesshistorie",
    "informasjon",
    "oppdateringsdato",
    "link",
    "kopidata",
]

# Fellesegenskaper_DelområdeType + DelområdeType (used by most area types)
DELOMRADE_PREFIX: list[str] = [
    "identifikasjon",
    "førsteDigitaliseringsdato",
    "oppdateringsdato",
    "kopidata",
    "arealplanId",
    "vertikalnivå",
]

# Fellesegenskaper_LinjerOgPunktType + LinjerOgPunktType (used by line/point types)
LINJER_OG_PUNKT_PREFIX: list[str] = [
    "identifikasjon",
    "førsteDigitaliseringsdato",
    "oppdateringsdato",
    "kvalitet",
    "kopidata",
    "arealplanId",
    "vertikalnivå",
]

# Kommuneplan (KP) prefixes — from kommuneplan_20190401_filprod.xsd
# Different element order from RP in Fellesegenskaper_PlanområdeType,
# and no vertikalnivå in DelområdeType/LinjerOgPunktType.

KP_PLANOMRADE_PREFIX: list[str] = [
    "identifikasjon",
    "førsteDigitaliseringsdato",
    "oppdateringsdato",
    "prosesshistorie",
    "informasjon",
    "kopidata",
    "link",
]

KP_DELOMRADE_PREFIX: list[str] = [
    "identifikasjon",
    "førsteDigitaliseringsdato",
    "oppdateringsdato",
    "kopidata",
    "arealplanId",
]

KP_LINJER_OG_PUNKT_PREFIX: list[str] = [
    "identifikasjon",
    "førsteDigitaliseringsdato",
    "oppdateringsdato",
    "kvalitet",
    "kopidata",
    "arealplanId",
]
