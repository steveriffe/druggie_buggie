#!/usr/bin/env python3
"""
SAMHSA TEDS-D (Discharges) Harvester & Revolving Door Pipeline for Druggie_buggie.
Downloads the official 2023 TEDS-D Public Use File bundle from SAMHSA:
https://www.samhsa.gov/data/system/files/media-puf-file/teds-d-2023-ds0001-bndl-data-csv_v1.zip
Extracts and filters for California (STFIPS=6) and Oregon (STFIPS=41).
Calculates Revolving Door metrics, stages data to BigQuery bronze, and deploys gold mart.
"""

import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import zipfile
import urllib.request
import json
import logging
import subprocess
import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

from src.analysis.revolving_door_metrics import RevolvingDoorAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "db1b-1"
TEDS_ZIP_URL = "https://www.samhsa.gov/data/system/files/media-puf-file/teds-d-2023-ds0001-bndl-data-csv_v1.zip"
ZIP_PATH = "data/raw/teds_d_2023.zip"
OUTPUT_JSON = "data/processed/teds_d_ca_or_2023.json"
METRICS_JSON = "data/processed/revolving_door_metrics.json"


def get_bigquery_client() -> bigquery.Client:
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()
    return bigquery.Client(project=PROJECT_ID, credentials=Credentials(token))


def download_teds():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    if os.path.exists(ZIP_PATH) and os.path.getsize(ZIP_PATH) > 1000000:
        logger.info(f"Using cached TEDS-D archive: {ZIP_PATH} ({os.path.getsize(ZIP_PATH):,} bytes)")
        return

    logger.info(f"Downloading SAMHSA TEDS-D 2023 from {TEDS_ZIP_URL}...")
    headers = {"User-Agent": "Mozilla/5.0 (Investigative Research; Druggie_buggie)"}
    req = urllib.request.Request(TEDS_ZIP_URL, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp, open(ZIP_PATH, "wb") as f:
        f.write(resp.read())
    logger.info(f"✅ Downloaded {ZIP_PATH} ({os.path.getsize(ZIP_PATH):,} bytes)")


def process_teds():
    logger.info("Extracting and filtering TEDS-D for CA (FIPS=6) and OR (FIPS=41)...")
    target_fips = {6, 41}
    
    with zipfile.ZipFile(ZIP_PATH) as z:
        csv_files = [f for f in z.namelist() if f.lower().endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError("No CSV found in TEDS-D zip")
        csv_name = csv_files[0]
        logger.info(f"Parsing {csv_name} from zip...")

        with z.open(csv_name) as f:
            # Read in chunks
            chunks = []
            chunksize = 100000
            for chunk in pd.read_csv(f, chunksize=chunksize, low_memory=False):
                chunk.columns = [c.upper() for c in chunk.columns]
                if "STFIPS" in chunk.columns:
                    filtered = chunk[chunk["STFIPS"].isin(target_fips)].copy()
                    if not filtered.empty:
                        chunks.append(filtered)
            
            df = pd.concat(chunks, ignore_index=True)
            logger.info(f"Total filtered CA & OR discharge records: {len(df):,}")

    # Standardize column names
    df.columns = [c.lower() for c in df.columns]
    if "noprior" in df.columns and "numprg" not in df.columns:
        df["numprg"] = df["noprior"]
    
    # Calculate Econometric Revolving Door Metrics
    metrics_by_payer = RevolvingDoorAnalyzer.calculate_recidivism_by_payer(df)
    overall_index = RevolvingDoorAnalyzer.calculate_revolving_door_index(df)

    logger.info("\n--- Revolving Door Index (CA & OR Combined) ---")
    logger.info(f"Total Discharge Episodes: {overall_index['total_episodes']:,}")
    logger.info(f"Episodes with >= 3 Prior Admissions: {overall_index['episodes_with_3plus_prior_stays']:,} ({overall_index['revolving_door_index_pct']}%)")
    logger.info(f"Total Early Dropouts / AMA: {overall_index['total_dropouts_ama']:,} ({overall_index['dropout_rate_pct']}%)")

    logger.info("\n--- Metrics by Primary Payment Source ---")
    print(metrics_by_payer.to_string(index=False))

    # Save metrics JSON for Visualization Dashboard
    metrics_export = {
        "overall": overall_index,
        "by_payer": metrics_by_payer.to_dict(orient="records"),
        "california_total": int((df["stfips"] == 6).sum()),
        "oregon_total": int((df["stfips"] == 41).sum()),
    }
    with open(METRICS_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics_export, f, indent=2)

    # Save sample processed records for BigQuery
    records = []
    sample_df = df.head(10000) # Stage top 10,000 for responsive Bronze staging
    for _, row in sample_df.iterrows():
        records.append({
            "discharge_year": 2023,
            "stfips": int(row.get("stfips", 0)) if pd.notna(row.get("stfips")) else None,
            "cbsa": int(row.get("cbsa", 0)) if pd.notna(row.get("cbsa")) else None,
            "services": int(row.get("services", 0)) if pd.notna(row.get("services")) else None,
            "reason": int(row.get("reason", 0)) if pd.notna(row.get("reason")) else None,
            "los": int(row.get("los", 0)) if pd.notna(row.get("los")) else None,
            "numprg": int(row.get("numprg", 0)) if pd.notna(row.get("numprg")) else None,
            "primpay": int(row.get("primpay", 0)) if pd.notna(row.get("primpay")) else None,
            "sub1": int(row.get("sub1", 0)) if pd.notna(row.get("sub1")) else None,
            "sub2": int(row.get("sub2", 0)) if pd.notna(row.get("sub2")) else None,
            "sub3": int(row.get("sub3", 0)) if pd.notna(row.get("sub3")) else None,
            "freq1": int(row.get("freq1", 0)) if pd.notna(row.get("freq1")) else None,
            "mstate": int(row.get("mstate", 0)) if pd.notna(row.get("mstate")) else None,
            "employ": int(row.get("employ", 0)) if pd.notna(row.get("employ")) else None,
            "living": int(row.get("living", 0)) if pd.notna(row.get("living")) else None,
            "raw_payload": json.dumps({k: v for k, v in row.to_dict().items() if pd.notna(v)}),
            "ingested_at": pd.Timestamp.utcnow().isoformat(),
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    return records


def stage_to_bigquery(records):
    client = get_bigquery_client()
    table_id = f"{PROJECT_ID}.rehab_bronze.raw_samhsa_teds_discharges"
    logger.info(f"Staging {len(records)} TEDS-D discharge records to {table_id}...")

    # Load DDL if table does not exist
    ddl_path = "sql/bronze/01_teds_discharges.sql"
    if os.path.exists(ddl_path):
        with open(ddl_path) as f:
            client.query(f.read()).result()

    # Load records in chunks
    chunksize = 1000
    for i in range(0, len(records), chunksize):
        chunk = records[i:i + chunksize]
        errs = client.insert_rows_json(table_id, chunk)
        if errs:
            logger.error(f"Error loading TEDS chunk: {errs}")
            return
    logger.info(f"✅ Staged {len(records):,} records to BigQuery {table_id}")

    # Deploy Gold Mart View
    gold_ddl = "sql/gold/01_mart_revolving_door.sql"
    if os.path.exists(gold_ddl):
        with open(gold_ddl) as f:
            client.query(f.read()).result()
        logger.info(f"✅ Deployed Gold Mart: `{PROJECT_ID}.rehab_gold.mart_revolving_door_attrition`")


if __name__ == "__main__":
    download_teds()
    records = process_teds()
    stage_to_bigquery(records)
