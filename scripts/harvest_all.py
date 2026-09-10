#!/usr/bin/env python3
"""
Unified Data Harvester for Druggie_buggie.
Downloads Tier 1 public datasets using Python standard library (urllib, json, csv):
1. California DHCS Licensed & Certified Residential SUD Facilities (2,266 records)
   - Filters and aggregates Orange County (Dana Point, Costa Mesa, Newport Beach, Huntington Beach, San Clemente, Laguna Beach, Santa Ana).
2. HHS-OIG List of Excluded Individuals and Entities (LEIE)
   - Downloads official LEIE CSV and filters for California (CA) and Oregon (OR).
3. SAMHSA N-SUMHSS / Treatment Facility Directory
"""

import os
import sys
import json
import csv
import urllib.request
import urllib.parse
from datetime import datetime

DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"

os.makedirs(DATA_RAW_DIR, exist_ok=True)
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)

OC_RIVIERA_CITIES = {
    "COSTA MESA",
    "NEWPORT BEACH",
    "HUNTINGTON BEACH",
    "SAN CLEMENTE",
    "LAGUNA BEACH",
    "DANA POINT",
    "SAN JUAN CAPISTRANO",
    "LAGUNA NIGUEL",
    "SANTA ANA",
    "IRVINE",
    "ANAHEIM",
}


def harvest_ca_dhcs():
    print("\n==================================================")
    print("🌴 1. Harvesting California DHCS SUD Facilities...")
    print("==================================================")
    resource_id = "7f7cc7f6-484c-4d0d-98d3-4b1ca091308a"
    base_url = "https://data.ca.gov/api/3/action/datastore_search"
    
    all_records = []
    limit = 1000
    offset = 0
    total = None
    
    headers = {"User-Agent": "Mozilla/5.0 (Investigative Data Harvester; contact: steve@riffe.co.uk)"}

    while total is None or offset < total:
        query_params = urllib.parse.urlencode({"resource_id": resource_id, "limit": limit, "offset": offset})
        url = f"{base_url}?{query_params}"
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data.get("success"):
                    print(f"API returned non-success: {data}")
                    break
                result = data.get("result", {})
                records = result.get("records", [])
                total = result.get("total", 0)
                all_records.extend(records)
                print(f"  Fetched {len(all_records)} / {total} records (offset {offset})...")
                offset += len(records)
                if not records:
                    break
        except Exception as e:
            print(f"Error fetching CA DHCS data: {e}")
            break

    # Save raw
    raw_path = os.path.join(DATA_RAW_DIR, "ca_dhcs_facilities_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)
    print(f"✅ Saved {len(all_records)} raw records to {raw_path}")

    # Standardize & Analyze
    oc_records = []
    statewide_capacity = 0
    oc_capacity = 0
    city_counts = {}
    ims_count = 0

    standardized = []
    now_ts = datetime.utcnow().isoformat()

    for rec in all_records:
        city = (rec.get("Facility_City") or "").strip().upper()
        county = (rec.get("CountyName") or "").strip()
        is_oc = "ORANGE" in county.upper()
        
        try:
            capacity = int(rec.get("Total_Capacity") or rec.get("Treatment_Capacity") or 0)
        except (ValueError, TypeError):
            capacity = 0

        statewide_capacity += capacity
        ims = (rec.get("Incident_Medical_Services") or "").strip().lower() == "yes"
        if ims:
            ims_count += 1

        if is_oc:
            oc_records.append(rec)
            oc_capacity += capacity
            city_counts[city] = city_counts.get(city, 0) + 1

        standardized.append({
            "source_agency": "CA_DHCS",
            "facility_name": rec.get("Facility_Name", "UNKNOWN"),
            "legal_entity_name": rec.get("Legal_Entity_Name", ""),
            "application_number": rec.get("Application_Number", ""),
            "license_number": rec.get("Application_Number", ""),
            "facility_type": rec.get("Type_of_Application", "Licensed"),
            "program_code": rec.get("Program_Code", ""),
            "licensed_capacity": capacity,
            "address_line": rec.get("Facility_Address1", ""),
            "address_line2": rec.get("Facility_Address2", ""),
            "city": rec.get("Facility_City", ""),
            "state": "CA",
            "zip_code": rec.get("Facility_Zip", ""),
            "county": county,
            "phone": rec.get("Facility_Phone", ""),
            "license_status": "Active" if rec.get("Lic_Expiration_Date") else "Unknown",
            "license_expiration": rec.get("Lic_Expiration_Date", ""),
            "incidental_medical_services": ims,
            "target_population": rec.get("Target_Population", ""),
            "latitude": rec.get("Latitude"),
            "longitude": rec.get("Longitude"),
            "is_oc_rehab_riviera": is_oc and (city in OC_RIVIERA_CITIES),
            "ingested_at": now_ts,
        })

    # Save standardized JSON
    std_path = os.path.join(DATA_PROCESSED_DIR, "ca_dhcs_facilities_standardized.json")
    with open(std_path, "w", encoding="utf-8") as f:
        json.dump(standardized, f, indent=2)

    # Save Orange County slice
    oc_path = os.path.join(DATA_PROCESSED_DIR, "orange_county_facilities.json")
    with open(oc_path, "w", encoding="utf-8") as f:
        json.dump(oc_records, f, indent=2)

    print("\n--- CA DHCS Summary ---")
    print(f"Total Facilities Statewide: {len(all_records)}")
    print(f"Total Bed Capacity Statewide: {statewide_capacity:,}")
    print(f"Facilities with Incidental Medical Services (IMS): {ims_count}")
    print(f"Orange County Facilities: {len(oc_records)}")
    print(f"Orange County Bed Capacity: {oc_capacity:,}")
    print("Orange County Top Municipalities:")
    for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {city}: {count} facilities")
    print(f"  - DANA POINT: {city_counts.get('DANA POINT', 0)} facilities")

    return len(all_records)


def harvest_hhs_oig_leie():
    print("\n==================================================")
    print("⚖️  2. Harvesting HHS-OIG List of Excluded Entities...")
    print("==================================================")
    leie_url = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"
    raw_leie_path = os.path.join(DATA_RAW_DIR, "hhs_oig_leie.csv")
    
    headers = {"User-Agent": "Mozilla/5.0 (Investigative Harvester)"}
    req = urllib.request.Request(leie_url, headers=headers)
    
    try:
        print("  Downloading official HHS-OIG LEIE database (~15MB)...")
        with urllib.request.urlopen(req, timeout=60) as resp, open(raw_leie_path, "wb") as out_file:
            out_file.write(resp.read())
        print(f"✅ Saved raw LEIE file to {raw_leie_path}")
    except Exception as e:
        print(f"Error downloading LEIE: {e}")
        return 0

    # Filter for CA and OR
    filtered_records = []
    ca_count = 0
    or_count = 0

    with open(raw_leie_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = (row.get("STATE") or "").strip().upper()
            if state in ("CA", "OR"):
                if state == "CA":
                    ca_count += 1
                elif state == "OR":
                    or_count += 1
                filtered_records.append({
                    "npi": row.get("NPI", "").strip(),
                    "last_name": row.get("LASTNAME", "").strip(),
                    "first_name": row.get("FIRSTNAME", "").strip(),
                    "mid_name": row.get("MIDNAME", "").strip(),
                    "bus_name": row.get("BUSNAME", "").strip(),
                    "general_specialty": row.get("GENERAL", "").strip(),
                    "specialty": row.get("SPECIALTY", "").strip(),
                    "upin": row.get("UPIN", "").strip(),
                    "address": row.get("ADDRESS", "").strip(),
                    "city": row.get("CITY", "").strip(),
                    "state": state,
                    "zip": row.get("ZIP", "").strip(),
                    "exclusion_type": row.get("EXCLTYPE", "").strip(),
                    "exclusion_date": row.get("EXCLDATE", "").strip(),
                    "reinstatement_date": row.get("REINDATE", "").strip(),
                    "waiver_date": row.get("WAIVERDATE", "").strip(),
                    "waiver_state": row.get("WVRSTATE", "").strip(),
                })

    proc_path = os.path.join(DATA_PROCESSED_DIR, "hhs_oig_exclusions_ca_or.json")
    with open(proc_path, "w", encoding="utf-8") as f:
        json.dump(filtered_records, f, indent=2)

    print("\n--- HHS-OIG LEIE Summary ---")
    print(f"Total CA Excluded Individuals & Entities: {ca_count:,}")
    print(f"Total OR Excluded Individuals & Entities: {or_count:,}")
    print(f"✅ Filtered {len(filtered_records):,} records saved to {proc_path}")
    return len(filtered_records)


if __name__ == "__main__":
    print("🚀 Starting Unified Data Harvester...")
    ca_count = harvest_ca_dhcs()
    leie_count = harvest_hhs_oig_leie()
    print("\n==================================================")
    print(f"🎉 Harvest Complete: {ca_count} DHCS facilities, {leie_count} CA/OR exclusions.")
    print("==================================================")
