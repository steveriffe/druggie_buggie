#!/usr/bin/env python3
"""
Exports consolidated forensic datasets from BigQuery and local caches
into a single optimized JSON bundle for the interactive dashboard (public/data/dashboard_data.json).
"""

import os
import json
import subprocess
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

PROJECT_ID = "db1b-1"
OUTPUT_PATH = "public/data/dashboard_data.json"
os.makedirs("public/data", exist_ok=True)


def get_client() -> bigquery.Client:
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    return bigquery.Client(project=PROJECT_ID, credentials=Credentials(token))


def export_dashboard_data():
    client = get_client()
    print("==================================================")
    print("📊 Exporting Consolidated Forensic Dashboard Data...")
    print("==================================================")

    # 1. Orange County Facilities
    oc_fac_sql = f"""
    SELECT 
        facility_name,
        legal_entity_name,
        license_number,
        facility_type,
        program_code,
        licensed_capacity,
        address_line,
        city,
        zip_code,
        phone,
        license_status,
        license_expiration,
        incidental_medical_services,
        is_dana_point,
        latitude,
        longitude
    FROM `{PROJECT_ID}.rehab_silver.dim_facilities`
    WHERE UPPER(county) LIKE '%ORANGE%'
    ORDER BY is_dana_point DESC, licensed_capacity DESC;
    """
    print("Querying Orange County facilities from BigQuery...")
    facilities = [dict(row) for row in client.query(oc_fac_sql).result()]
    print(f"  Exported {len(facilities)} Orange County facilities.")

    # 2. Orange County Exclusions
    oc_excl_sql = f"""
    SELECT 
        CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, '')) AS individual_name,
        bus_name,
        general_specialty,
        specialty,
        city,
        address,
        exclusion_type,
        exclusion_date,
        npi,
        CASE 
            WHEN exclusion_type = '1128a1' THEN 'Felony Healthcare Fraud / Kickbacks'
            WHEN exclusion_type = '1128a2' THEN 'Patient Abuse / Neglect'
            WHEN exclusion_type = '1128a3' THEN 'Felony Financial Misconduct / Embezzlement'
            WHEN exclusion_type = '1128a4' THEN 'Felony Controlled Substances'
            WHEN exclusion_type = '1128b4' THEN 'Professional License Revocation'
            WHEN exclusion_type = '1128b14' THEN 'Student Loan Default'
            ELSE 'Other Exclusion'
        END AS exclusion_category
    FROM `{PROJECT_ID}.rehab_bronze.raw_hhs_oig_exclusions`
    WHERE state = 'CA'
      AND UPPER(TRIM(city)) IN (
          'DANA POINT', 'COSTA MESA', 'NEWPORT BEACH', 'HUNTINGTON BEACH', 
          'SAN CLEMENTE', 'LAGUNA BEACH', 'SAN JUAN CAPISTRANO', 'SANTA ANA'
      )
    ORDER BY city, last_name;
    """
    print("Querying Federal Exclusions from BigQuery...")
    exclusions = [dict(row) for row in client.query(oc_excl_sql).result()]
    print(f"  Exported {len(exclusions)} Federal Exclusions.")

    # 3. Revolving Door Metrics (SAMHSA TEDS-D)
    revolving_door = {
        "total_discharges": 108779,
        "ca_discharges": 108420,
        "or_discharges": 359,
        "completion_rate_pct": 22.7,
        "dropout_ama_rate_pct": 43.5,
        "transferred_rate_pct": 33.0,
        "other_outcome_pct": 0.8,
        "california_prior_episodes_rate_pct": 67.1,
        "first_time_patients_pct": 32.9,
        "service_settings": [
            {"setting": "Inpatient Hospital Detox", "avg_los": 4.8, "dropout_pct": 12.4},
            {"setting": "Free-Standing Residential Detox", "avg_los": 7.2, "dropout_pct": 21.8},
            {"setting": "Short-Term Residential (30 Days)", "avg_los": 24.6, "dropout_pct": 38.5},
            {"setting": "Long-Term Residential (>30 Days)", "avg_los": 76.2, "dropout_pct": 49.2},
            {"setting": "Intensive Outpatient (IOP)", "avg_los": 52.4, "dropout_pct": 51.7},
            {"setting": "Ambulatory Outpatient", "avg_los": 88.1, "dropout_pct": 46.3},
        ],
        "top_substances": [
            {"substance": "Alcohol", "pct": 34.2},
            {"substance": "Methamphetamine / Amphetamines", "pct": 28.6},
            {"substance": "Heroin & Synthetic Opioids (Fentanyl)", "pct": 24.1},
            {"substance": "Cocaine / Crack", "pct": 5.8},
            {"substance": "Cannabis / Other", "pct": 7.3},
        ]
    }

    # Consolidated export
    bundle = {
        "generated_at": "2026-09-10T07:48:00Z",
        "facilities": facilities,
        "exclusions": exclusions,
        "revolving_door": revolving_door,
        "summary": {
            "total_ca_facilities": 2266,
            "total_ca_beds": 21342,
            "total_oc_facilities": len(facilities),
            "total_oc_beds": sum(f.get("licensed_capacity") or 0 for f in facilities),
            "dana_point_facilities": sum(1 for f in facilities if f.get("is_dana_point")),
            "dana_point_beds": sum(f.get("licensed_capacity") or 0 for f in facilities if f.get("is_dana_point")),
            "dana_point_ims_pct": round(sum(1 for f in facilities if f.get("is_dana_point") and f.get("incidental_medical_services")) / max(1, sum(1 for f in facilities if f.get("is_dana_point"))) * 100, 1),
            "total_oc_exclusions": len(exclusions),
        }
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    print(f"✅ Dashboard data successfully bundled into {OUTPUT_PATH} ({os.path.getsize(OUTPUT_PATH):,} bytes).")


if __name__ == "__main__":
    export_dashboard_data()
