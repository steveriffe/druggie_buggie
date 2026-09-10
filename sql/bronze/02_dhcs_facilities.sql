-- ==============================================================================
-- Table: rehab_bronze.raw_dhcs_facilities
-- Description: Raw California Department of Health Care Services (DHCS) Licensed & Certified
--              Residential SUD Facilities and Orange County Municipal registries
-- ==============================================================================

CREATE TABLE IF NOT EXISTS `db1b-1.rehab_bronze.raw_dhcs_facilities` (
    source_agency STRING OPTIONS(description="Reporting authority (e.g. CA_DHCS, OC_MUNICIPAL, OR_OHA)"),
    facility_name STRING OPTIONS(description="Licensed facility / DBA name"),
    legal_entity_name STRING OPTIONS(description="Corporate entity or operator holding the license"),
    license_number STRING OPTIONS(description="State regulatory license number"),
    facility_type STRING OPTIONS(description="Licensed program type (e.g. Residential, Detox, Incidental Medical Services)"),
    licensed_capacity INT64 OPTIONS(description="Total authorized adult resident bed capacity"),
    address_line STRING OPTIONS(description="Street address of the facility"),
    city STRING OPTIONS(description="City (e.g. Costa Mesa, Newport Beach, Dana Point)"),
    state STRING OPTIONS(description="State abbreviation (CA, OR)"),
    zip_code STRING OPTIONS(description="Postal code"),
    county STRING OPTIONS(description="County (e.g. Orange, Los Angeles, Multnomah)"),
    license_status STRING OPTIONS(description="Status (Active, Revoked, Suspended, Probationary)"),
    disciplinary_flag BOOL OPTIONS(description="True if cited or sanctioned under HSC 11831.7 or state action"),
    raw_payload JSON OPTIONS(description="Raw source record payload"),
    ingested_at TIMESTAMP OPTIONS(description="Record ingestion timestamp")
)
CLUSTER BY county, city, license_status;
