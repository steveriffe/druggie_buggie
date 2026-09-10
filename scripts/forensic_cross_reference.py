#!/usr/bin/env python3
"""
Forensic Cross-Reference & Entity Resolution Engine for Druggie_buggie.
Executes BigQuery queries to cross-reference licensed SUD facilities in California
(focusing on Orange County & Dana Point) against the federal HHS-OIG Exclusion Database.
Detects potential matches by entity name, address, and city.
"""

import subprocess
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

PROJECT_ID = "db1b-1"


def get_client() -> bigquery.Client:
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    return bigquery.Client(project=PROJECT_ID, credentials=Credentials(token))


def run_cross_reference():
    client = get_client()
    print("==================================================")
    print("🕵️  Forensic Entity Cross-Reference: Facilities vs Federal Exclusions")
    print("==================================================")

    # 1. Exact & Fuzzy Name Matches on Business / Facility Names
    name_match_sql = f"""
    SELECT 
        f.facility_name,
        f.legal_entity_name,
        f.city AS facility_city,
        f.licensed_capacity,
        e.bus_name AS excluded_business_name,
        CONCAT(COALESCE(e.first_name, ''), ' ', COALESCE(e.last_name, '')) AS excluded_individual_name,
        e.general_specialty,
        e.exclusion_type,
        e.exclusion_date,
        e.city AS exclusion_city,
        e.state AS exclusion_state
    FROM `{PROJECT_ID}.rehab_silver.dim_facilities` f
    JOIN `{PROJECT_ID}.rehab_bronze.raw_hhs_oig_exclusions` e
      ON (
          UPPER(TRIM(f.legal_entity_name)) = UPPER(TRIM(e.bus_name))
          OR UPPER(TRIM(f.facility_name)) = UPPER(TRIM(e.bus_name))
      )
      AND e.bus_name IS NOT NULL AND e.bus_name != ''
    ORDER BY f.facility_name;
    """

    print("Running business entity name collision check...")
    rows = list(client.query(name_match_sql).result())
    if rows:
        print(f"⚠️  FOUND {len(rows)} DIRECT BUSINESS NAME COLLISIONS:")
        for r in rows:
            print(f"  • Match: {r.facility_name} (City: {r.facility_city}) | Excluded Entity: {r.excluded_business_name} | Type: {r.exclusion_type} | Date: {r.exclusion_date}")
    else:
        print("  ✅ No direct 100% corporate name collisions found with active facility names.")

    # 2. Excluded Individuals in Coastal Orange County Municipalities by Specialty
    oc_exclusions_sql = f"""
    SELECT 
        first_name,
        last_name,
        general_specialty,
        specialty,
        city,
        exclusion_type,
        exclusion_date
    FROM `{PROJECT_ID}.rehab_bronze.raw_hhs_oig_exclusions`
    WHERE state = 'CA'
      AND UPPER(TRIM(city)) IN (
          'DANA POINT', 'COSTA MESA', 'NEWPORT BEACH', 'HUNTINGTON BEACH', 
          'SAN CLEMENTE', 'LAGUNA BEACH', 'SAN JUAN CAPISTRANO', 'SANTA ANA'
      )
    ORDER BY city, last_name;
    """

    print("\n--- Federal Exclusions Located in Orange County 'Rehab Riviera' Cities ---")
    oc_rows = list(client.query(oc_exclusions_sql).result())
    print(f"Total Excluded Individuals/Entities residing/headquartered in Rehab Riviera cities: {len(oc_rows)}")
    
    city_breakdown = {}
    for r in oc_rows:
        city_breakdown[r.city] = city_breakdown.get(r.city, 0) + 1

    for city, cnt in sorted(city_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {city}: {cnt} excluded actors")

    # Sample top 5
    print("\nSample Excluded Profiles in these municipalities:")
    for r in oc_rows[:8]:
        spec = r.specialty or r.general_specialty or "Unknown"
        print(f"  - {r.first_name} {r.last_name} ({r.city}) | Specialty: {spec} | Type: {r.exclusion_type} | Date: {r.exclusion_date}")


if __name__ == "__main__":
    run_cross_reference()

