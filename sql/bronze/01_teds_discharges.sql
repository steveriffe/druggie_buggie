-- ==============================================================================
-- Table: rehab_bronze.raw_samhsa_teds_discharges
-- Description: Raw client-level substance use treatment discharge records from SAMHSA TEDS-D
-- Partitioning: Ingestion timestamp or year
-- ==============================================================================

CREATE TABLE IF NOT EXISTS `db1b-1.rehab_bronze.raw_samhsa_teds_discharges` (
    discharge_year INT64 OPTIONS(description="Reporting year of discharge"),
    stfips INT64 OPTIONS(description="State FIPS code (06=California, 41=Oregon)"),
    cbsa INT64 OPTIONS(description="Core Based Statistical Area code"),
    services INT64 OPTIONS(description="Service setting at admission/discharge (detox, residential, outpatient)"),
    reason INT64 OPTIONS(description="Reason for discharge (1=Treatment completed, 2=Dropped out / AMA, etc.)"),
    los INT64 OPTIONS(description="Length of stay in days"),
    numprg INT64 OPTIONS(description="Number of prior treatment episodes (0, 1, 2, 3, 4, 5+)"),
    primpay INT64 OPTIONS(description="Expected primary source of payment (Private insurance, Medicaid, etc.)"),
    sub1 INT64 OPTIONS(description="Primary substance of abuse"),
    sub2 INT64 OPTIONS(description="Secondary substance of abuse"),
    sub3 INT64 OPTIONS(description="Tertiary substance of abuse"),
    freq1 INT64 OPTIONS(description="Frequency of use of primary substance"),
    mstate INT64 OPTIONS(description="Marital status"),
    employ INT64 OPTIONS(description="Employment status at discharge"),
    living INT64 OPTIONS(description="Living arrangement at discharge"),
    raw_payload JSON OPTIONS(description="Raw record JSON payload"),
    ingested_at TIMESTAMP OPTIONS(description="Timestamp when record was loaded into BigQuery")
)
PARTITION BY RANGE_BUCKET(discharge_year, GENERATE_ARRAY(2015, 2030, 1))
CLUSTER BY stfips, reason, numprg;
