#!/usr/bin/env python3
"""
BigQuery Ingestion & Lakehouse Staging Pipeline for Druggie_buggie.
Creates Bronze, Silver, and Gold datasets in Google Cloud project db1b-1.
Loads harvested Tier 1 datasets (CA DHCS Facilities & HHS-OIG Exclusions).
Deploys Silver dimension views with Orange County and Dana Point flags.
"""

import os
import json
import logging
import subprocess
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2.credentials import Credentials

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "db1b-1"
LOCATION = "us-west1"

DATASETS = ["rehab_bronze", "rehab_silver", "rehab_gold"]


def get_bigquery_client() -> bigquery.Client:
    """Initialize BigQuery client with automatic gcloud token fallback."""
    try:
        token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
        creds = Credentials(token)
        return bigquery.Client(project=PROJECT_ID, credentials=creds)
    except Exception as e:
        logger.warning(f"Could not use gcloud token: {e}. Falling back to default credentials.")
        return bigquery.Client(project=PROJECT_ID)


def setup_datasets(client: bigquery.Client):
    """Create bronze, silver, and gold datasets if they don't exist."""
    print("==================================================")
    print(f"🏗️  Setting up BigQuery datasets in {PROJECT_ID} ({LOCATION})...")
    print("==================================================")
    for ds_name in DATASETS:
        dataset_id = f"{PROJECT_ID}.{ds_name}"
        try:
            client.get_dataset(dataset_id)
            print(f"  Dataset {dataset_id} already exists.")
        except NotFound:
            ds = bigquery.Dataset(dataset_id)
            ds.location = LOCATION
            client.create_dataset(ds, timeout=30)
            print(f"  ✅ Created dataset {dataset_id}")


def stage_ca_dhcs_facilities(client: bigquery.Client):
    """Load standardized CA DHCS facilities into rehab_bronze.raw_dhcs_facilities."""
    json_path = "data/processed/ca_dhcs_facilities_standardized.json"
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    print("\n==================================================")
    print("🏥 Staging California DHCS Facilities into BigQuery Bronze...")
    print("==================================================")

    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    table_id = f"{PROJECT_ID}.rehab_bronze.raw_dhcs_facilities"

    schema = [
        bigquery.SchemaField("source_agency", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("facility_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("legal_entity_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("application_number", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("license_number", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("facility_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("program_code", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("licensed_capacity", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("address_line", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("address_line2", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("zip_code", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("county", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("license_status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("license_expiration", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("incidental_medical_services", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("target_population", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("latitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("longitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("is_oc_rehab_riviera", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.clustering_fields = ["county", "city"]
    
    # Overwrite/recreate for clean staging
    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table)
    print(f"  Created table {table_id} with clustering on (county, city).")

    # Load in chunks of 500 rows
    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        errors = client.insert_rows_json(table_id, chunk)
        if errors:
            print(f"  ❌ Error loading chunk {i}: {errors}")
            return
    print(f"  ✅ Successfully staged {len(records)} records into {table_id}.")


def stage_hhs_oig_exclusions(client: bigquery.Client):
    """Load HHS-OIG Exclusions into rehab_bronze.raw_hhs_oig_exclusions."""
    json_path = "data/processed/hhs_oig_exclusions_ca_or.json"
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    print("\n==================================================")
    print("⚖️  Staging HHS-OIG LEIE Exclusions into BigQuery Bronze...")
    print("==================================================")

    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    table_id = f"{PROJECT_ID}.rehab_bronze.raw_hhs_oig_exclusions"

    schema = [
        bigquery.SchemaField("npi", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("last_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("first_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("mid_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("bus_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("general_specialty", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("specialty", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("upin", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("zip", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("exclusion_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("exclusion_date", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("reinstatement_date", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("waiver_date", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("waiver_state", "STRING", mode="NULLABLE"),
    ]

    table = bigquery.Table(table_id, schema=schema)
    table.clustering_fields = ["state", "city"]

    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table)
    print(f"  Created table {table_id} with clustering on (state, city).")

    chunk_size = 1000
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        errors = client.insert_rows_json(table_id, chunk)
        if errors:
            print(f"  ❌ Error loading exclusions chunk {i}: {errors}")
            return
    print(f"  ✅ Successfully staged {len(records)} records into {table_id}.")


def deploy_silver_views(client: bigquery.Client):
    """Deploy Silver standardized view."""
    print("\n==================================================")
    print("🥈 Deploying Silver Standardized Views...")
    print("==================================================")

    view_sql = f"""
    CREATE OR REPLACE VIEW `{PROJECT_ID}.rehab_silver.dim_facilities` AS
    SELECT
        FARM_FINGERPRINT(CONCAT(UPPER(TRIM(facility_name)), UPPER(TRIM(COALESCE(address_line, ''))), UPPER(TRIM(COALESCE(city, ''))))) AS facility_sk,
        source_agency,
        TRIM(facility_name) AS facility_name,
        TRIM(legal_entity_name) AS legal_entity_name,
        TRIM(license_number) AS license_number,
        facility_type,
        program_code,
        licensed_capacity,
        TRIM(address_line) AS address_line,
        TRIM(address_line2) AS address_line2,
        INITCAP(TRIM(city)) AS city,
        UPPER(TRIM(state)) AS state,
        SUBSTR(TRIM(zip_code), 1, 5) AS zip_code,
        INITCAP(TRIM(county)) AS county,
        phone,
        license_status,
        license_expiration,
        incidental_medical_services,
        target_population,
        latitude,
        longitude,
        CASE 
            WHEN UPPER(TRIM(county)) LIKE '%ORANGE%' AND UPPER(TRIM(city)) IN (
                'COSTA MESA', 'NEWPORT BEACH', 'HUNTINGTON BEACH', 'SAN CLEMENTE', 
                'LAGUNA BEACH', 'DANA POINT', 'SAN JUAN CAPISTRANO', 'LAGUNA NIGUEL', 
                'SANTA ANA', 'IRVINE', 'ANAHEIM'
            ) THEN TRUE 
            ELSE FALSE 
        END AS is_oc_rehab_riviera,
        CASE 
            WHEN UPPER(TRIM(city)) = 'DANA POINT' THEN TRUE 
            ELSE FALSE 
        END AS is_dana_point,
        ingested_at
    FROM `{PROJECT_ID}.rehab_bronze.raw_dhcs_facilities`;
    """

    job = client.query(view_sql)
    job.result()
    print(f"  ✅ Deployed view `{PROJECT_ID}.rehab_silver.dim_facilities` with Dana Point and Rehab Riviera flags.")


def run_forensic_checks(client: bigquery.Client):
    """Run initial investigative and verification queries."""
    print("\n==================================================")
    print("🔍 Running Forensic Verification Queries...")
    print("==================================================")

    # 1. Dana Point facilities
    dp_sql = f"""
    SELECT facility_name, legal_entity_name, program_code, licensed_capacity, incidental_medical_services, address_line
    FROM `{PROJECT_ID}.rehab_silver.dim_facilities`
    WHERE is_dana_point = TRUE
    ORDER BY licensed_capacity DESC;
    """
    print("\n--- Dana Point, CA Licensed SUD Facilities ---")
    dp_rows = list(client.query(dp_sql).result())
    for r in dp_rows:
        ims_tag = "IMS (Detox)" if r.incidental_medical_services else "Residential Only"
        print(f"  • {r.facility_name} | Beds: {r.licensed_capacity} | {ims_tag} | Operator: {r.legal_entity_name} | {r.address_line}")

    # 2. Orange County vs Statewide Summary
    oc_summary_sql = f"""
    SELECT 
        COUNT(1) as total_facilities,
        SUM(licensed_capacity) as total_beds,
        COUNTIF(incidental_medical_services) as total_ims_detox,
        ROUND(AVG(licensed_capacity), 1) as avg_beds_per_facility
    FROM `{PROJECT_ID}.rehab_silver.dim_facilities`
    WHERE is_oc_rehab_riviera = TRUE;
    """
    row = list(client.query(oc_summary_sql).result())[0]
    print("\n--- Orange County 'Rehab Riviera' Corridor Totals ---")
    print(f"  Facilities: {row.total_facilities} | Total Beds: {row.total_beds:,} | IMS Detox Facilities: {row.total_ims_detox} | Avg Bed Size: {row.avg_beds_per_facility}")


if __name__ == "__main__":
    client = get_bigquery_client()
    setup_datasets(client)
    stage_ca_dhcs_facilities(client)
    stage_hhs_oig_exclusions(client)
    deploy_silver_views(client)
    run_forensic_checks(client)
    print("\n==================================================")
    print("🎉 BigQuery Staging and Verification Complete!")
    print("==================================================")
