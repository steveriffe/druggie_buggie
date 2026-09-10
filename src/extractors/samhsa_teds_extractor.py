"""
SAMHSA TEDS-D (Treatment Episode Data Set - Discharges) Extractor.
Processes annual discharge microdata to extract key variables:
- NUMPRG: Number of prior treatment episodes (revolving door indicator)
- REASON: Reason for discharge (completed treatment vs dropped out / AMA)
- LOS: Length of stay in days
- PRIMPAY: Payment source (Private insurance, Medicaid, self-pay)
- SERVICES: Service setting (detoxification, residential rehabilitation, ambulatory outpatient)
Filtered for California (STFIPS=6) and Oregon (STFIPS=41).
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# FIPS codes
FIPS_CALIFORNIA = 6
FIPS_OREGON = 41


class SAMHSATEDSExtractor:
    """Extracts and filters SAMHSA TEDS-D microdata files."""

    def __init__(self, target_fips: Optional[List[int]] = None):
        self.target_fips = target_fips or [FIPS_CALIFORNIA, FIPS_OREGON]

    def parse_csv(self, file_path: str, discharge_year: int = 2021) -> List[Dict[str, Any]]:
        """
        Parse raw TEDS-D CSV file, filtering by state FIPS to keep memory low.
        Returns rows formatted for BigQuery bronze raw_samhsa_teds_discharges table.
        """
        logger.info(f"Loading TEDS-D file {file_path} for year {discharge_year}...")
        now_ts = datetime.utcnow().isoformat()
        
        # Read in chunks to handle multi-gigabyte national files safely
        bronze_rows = []
        chunk_size = 50000
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
            # Normalize column names to lowercase
            chunk.columns = [c.lower() for c in chunk.columns]
            
            # Filter by state FIPS if available
            if "stfips" in chunk.columns:
                filtered = chunk[chunk["stfips"].isin(self.target_fips)]
            else:
                filtered = chunk

            for _, row in filtered.iterrows():
                row_dict = row.to_dict()
                bronze_rows.append({
                    "discharge_year": discharge_year,
                    "stfips": int(row_dict.get("stfips", 0)) if pd.notna(row_dict.get("stfips")) else None,
                    "cbsa": int(row_dict.get("cbsa", 0)) if pd.notna(row_dict.get("cbsa")) else None,
                    "services": int(row_dict.get("services", 0)) if pd.notna(row_dict.get("services")) else None,
                    "reason": int(row_dict.get("reason", 0)) if pd.notna(row_dict.get("reason")) else None,
                    "los": int(row_dict.get("los", 0)) if pd.notna(row_dict.get("los")) else None,
                    "numprg": int(row_dict.get("numprg", 0)) if pd.notna(row_dict.get("numprg")) else None,
                    "primpay": int(row_dict.get("primpay", 0)) if pd.notna(row_dict.get("primpay")) else None,
                    "sub1": int(row_dict.get("sub1", 0)) if pd.notna(row_dict.get("sub1")) else None,
                    "sub2": int(row_dict.get("sub2", 0)) if pd.notna(row_dict.get("sub2")) else None,
                    "sub3": int(row_dict.get("sub3", 0)) if pd.notna(row_dict.get("sub3")) else None,
                    "freq1": int(row_dict.get("freq1", 0)) if pd.notna(row_dict.get("freq1")) else None,
                    "mstate": int(row_dict.get("mstate", 0)) if pd.notna(row_dict.get("mstate")) else None,
                    "employ": int(row_dict.get("employ", 0)) if pd.notna(row_dict.get("employ")) else None,
                    "living": int(row_dict.get("living", 0)) if pd.notna(row_dict.get("living")) else None,
                    "raw_payload": json.dumps({k: v for k, v in row_dict.items() if pd.notna(v)}),
                    "ingested_at": now_ts,
                })

        logger.info(f"Filtered {len(bronze_rows)} records for states {self.target_fips}.")
        return bronze_rows
