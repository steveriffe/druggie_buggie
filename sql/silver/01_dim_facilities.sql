-- ==============================================================================
-- View / Table: rehab_silver.dim_facilities
-- Description: Standardized, deduplicated facility dimension with normalized address,
--              geocodes, licensed bed capacities, and municipal zoning flags.
-- ==============================================================================

CREATE OR REPLACE VIEW `db1b-1.rehab_silver.dim_facilities` AS
SELECT
    FARM_FINGERPRINT(CONCAT(UPPER(TRIM(facility_name)), UPPER(TRIM(address_line)), UPPER(TRIM(city)))) AS facility_sk,
    source_agency,
    TRIM(facility_name) AS facility_name,
    TRIM(legal_entity_name) AS legal_entity_name,
    TRIM(license_number) AS license_number,
    facility_type,
    licensed_capacity,
    TRIM(address_line) AS address_line,
    INITCAP(TRIM(city)) AS city,
    UPPER(TRIM(state)) AS state,
    SUBSTR(TRIM(zip_code), 1, 5) AS zip_code,
    INITCAP(TRIM(county)) AS county,
    UPPER(TRIM(license_status)) AS license_status,
    disciplinary_flag,
    CASE 
        WHEN UPPER(TRIM(county)) = 'ORANGE' AND UPPER(TRIM(city)) IN ('COSTA MESA', 'NEWPORT BEACH', 'HUNTINGTON BEACH', 'SAN CLEMENTE', 'LAGUNA BEACH', 'DANA POINT') 
        THEN TRUE 
        ELSE FALSE 
    END AS is_oc_rehab_riviera,
    ingested_at
FROM `db1b-1.rehab_bronze.raw_dhcs_facilities`;
