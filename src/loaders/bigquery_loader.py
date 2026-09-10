"""
BigQuery loader module for Druggie_buggie.
Manages dataset initialization and table loading in Google Cloud project db1b-1.
"""

import logging
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_PROJECT_ID = "db1b-1"
DEFAULT_LOCATION = "us-west1"


class BigQueryLakehouse:
    """Interface for managing BigQuery bronze, silver, and gold datasets."""

    def __init__(self, project_id: str = DEFAULT_PROJECT_ID, location: str = DEFAULT_LOCATION):
        self.project_id = project_id
        self.location = location
        self.client = bigquery.Client(project=self.project_id)

    def ensure_dataset(self, dataset_name: str) -> bigquery.Dataset:
        """Create dataset if it does not already exist."""
        dataset_id = f"{self.project_id}.{dataset_name}"
        try:
            dataset = self.client.get_dataset(dataset_id)
            logger.info(f"Dataset {dataset_id} already exists.")
            return dataset
        except NotFound:
            logger.info(f"Creating dataset {dataset_id} in {self.location}...")
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = self.location
            return self.client.create_dataset(dataset, timeout=30)

    def load_records(self, dataset_name: str, table_name: str, records: List[Dict[str, Any]]) -> None:
        """Insert records into target table using JSON insert."""
        if not records:
            logger.warning(f"No records provided for {dataset_name}.{table_name}.")
            return

        table_id = f"{self.project_id}.{dataset_name}.{table_name}"
        logger.info(f"Inserting {len(records)} records into {table_id}...")
        errors = self.client.insert_rows_json(table_id, records)
        if errors:
            logger.error(f"Failed to insert rows: {errors}")
            raise RuntimeError(f"BigQuery insert error: {errors}")
        logger.info(f"Successfully inserted {len(records)} rows into {table_id}.")

    def execute_sql(self, sql_query: str) -> bigquery.table.RowIterator:
        """Execute arbitrary DDL / DML in BigQuery."""
        logger.info("Executing BigQuery job...")
        query_job = self.client.query(sql_query)
        return query_job.result()

