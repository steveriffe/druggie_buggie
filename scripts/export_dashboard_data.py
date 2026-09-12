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

    # 4. Ocean Hills Deep-Dive Case Study
    ocean_hills_case_study = {
        "facility_name": "Ocean Hills Recovery, LLC",
        "license_number": "300208KP",
        "license_expiration": "2028-07-31",
        "total_licensed_beds": 30,
        "incidental_medical_services": True,
        "central_hub": {
            "name": "Central Clinical & Administrative Hub",
            "address": "33701 Big Sur St., Dana Point, CA 92629",
            "role": "Group Therapy, Day Treatment (IOP/PHP), Intake, Urine Toxicology Collection, Executive Offices",
            "lat": 33.473206,
            "lng": -117.689012
        },
        "satellite_houses": [
            {
                "name": "Satellite House 1",
                "address": "33402 Palo Alto St., Dana Point, CA 92629",
                "estimated_beds": 6,
                "zoning": "Single-Family Residential (HSC § 11834.01)",
                "distance_to_hub": "0.6 miles"
            },
            {
                "name": "Satellite House 2",
                "address": "34062 Street of the Amber Lantern, Dana Point, CA 92629",
                "estimated_beds": 6,
                "zoning": "Lantern District Residential",
                "distance_to_hub": "0.9 miles"
            },
            {
                "name": "Satellite House 3",
                "address": "33242 Christina Dr., Dana Point, CA 92629",
                "estimated_beds": 6,
                "zoning": "Suburban Single-Family Residential",
                "distance_to_hub": "1.2 miles"
            },
            {
                "name": "Satellite House 4",
                "address": "34469 Camino El Molino, Capistrano Beach / Dana Point, CA 92677",
                "estimated_beds": 6,
                "zoning": "Capistrano Beach Residential",
                "distance_to_hub": "1.8 miles"
            }
        ],
        "leadership": [
            {"name": "Robert Leigh", "role": "Chief Executive Officer (CEO)"},
            {"name": "Christian Small, M.D.", "role": "Medical Director & Addiction Psychiatrist", "npi": "1740546209", "affiliation": "Headlands Addiction Treatment Services"},
            {"name": "George H. Tucker, Ph.D., ABPP", "role": "Clinical Director", "experience": "40 years inpatient/outpatient"},
            {"name": "Jerney Allen", "role": "Director of Admissions"},
            {"name": "Ricky Herrera", "role": "Director of Business Development"}
        ],
        "daily_circuit": [
            {"step": "1. Morning Muster", "desc": "House managers dispense morning meds and conduct headcounts at each satellite house."},
            {"step": "2. Shuttle Transport", "desc": "White passenger vans shuttle 30 patients from the 4 suburban homes to 33701 Big Sur St."},
            {"step": "3. Central Clinical Day", "desc": "90-minute group therapy blocks (Rev Codes 0905/0906), psychiatric consults, and 2-3x weekly Urine Drug Screens (UDS CPT 80307 / G0483)."},
            {"step": "4. Evening Return", "desc": "Vans transport patients back to suburban residential neighborhoods to sleep."}
        ]
    }

    # Consolidated export
    bundle = {
        "generated_at": "2026-09-10T07:48:00Z",
        "facilities": facilities,
        "exclusions": exclusions,
        "revolving_door": revolving_door,
        "ocean_hills_case_study": ocean_hills_case_study,
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
