"""
California DHCS Licensed and Certified Residential and Outpatient Facilities Harvester.
Extracts facility records from California Open Data (data.ca.gov / CHHS) with deep focus
on Orange County municipalities (Costa Mesa, Newport Beach, Huntington Beach, San Clemente,
Laguna Beach, Dana Point, Santa Ana).
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# CA CHHS / data.ca.gov Socrata endpoint for DHCS licensed SUD facilities
# Dataset ID: residential and outpatient SUD treatment facilities
CHHS_SOCRATA_ENDPOINT = "https://data.ca.gov/api/3/action/datastore_search"
DHCS_PORTAL_RESOURCE_ID = "087c53d9-6059-47fe-bb03-c15c898c1a63"

OC_RIVIERA_CITIES = [
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
]


class CADHCSExtractor:
    """Extracts licensed SUD treatment facility records from California open data repositories."""

    def __init__(self, resource_id: str = DHCS_PORTAL_RESOURCE_ID):
        self.resource_id = resource_id

    def fetch_records(self, limit: int = 5000, county: str = "Orange") -> List[Dict[str, Any]]:
        """Fetch records from California Open Data via CKAN/Socrata query."""
        logger.info(f"Querying CA DHCS facilities for county={county} (limit={limit})...")
        params = {
            "resource_id": self.resource_id,
            "limit": limit,
        }
        if county:
            params["q"] = county

        try:
            resp = requests.get(CHHS_SOCRATA_ENDPOINT, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") and "records" in data.get("result", {}):
                records = data["result"]["records"]
                logger.info(f"Retrieved {len(records)} records from CA Open Data API.")
                return records
            else:
                logger.warning(f"Unexpected response format: {data}")
                return []
        except Exception as e:
            logger.error(f"Error fetching from CA Open Data: {e}")
            return []

    def transform_to_bronze_schema(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map raw portal records to BigQuery bronze schema format."""
        bronze_rows = []
        now_ts = datetime.utcnow().isoformat()

        for rec in raw_records:
            # Map standard fields flexibly based on CA dataset field naming
            city = rec.get("facility_city") or rec.get("city", "")
            county = rec.get("county") or rec.get("facility_county", "")
            capacity_raw = rec.get("capacity") or rec.get("licensed_capacity") or 0
            try:
                capacity = int(capacity_raw)
            except (ValueError, TypeError):
                capacity = 0

            transformed = {
                "source_agency": "CA_DHCS",
                "facility_name": rec.get("facility_name") or rec.get("program_name", "UNKNOWN"),
                "legal_entity_name": rec.get("corporate_name") or rec.get("legal_name") or rec.get("facility_name", ""),
                "license_number": str(rec.get("license_number") or rec.get("facility_number", "")),
                "facility_type": rec.get("service_type") or rec.get("facility_type", "Residential"),
                "licensed_capacity": capacity,
                "address_line": rec.get("facility_address") or rec.get("address", ""),
                "city": city,
                "state": "CA",
                "zip_code": str(rec.get("facility_zip") or rec.get("zip", "")),
                "county": county,
                "license_status": rec.get("facility_status") or rec.get("status", "Active"),
                "disciplinary_flag": False,
                "raw_payload": json.dumps(rec),
                "ingested_at": now_ts,
            }
            bronze_rows.append(transformed)

        return bronze_rows


if __name__ == "__main__":
    extractor = CADHCSExtractor()
    records = extractor.fetch_records(limit=100)
    print(f"Sample transformed records: {len(records)}")
