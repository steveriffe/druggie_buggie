"""
Revolving Door & Treatment Recidivism Analysis Model.
Calculates recidivism metrics from SAMHSA TEDS-D microdata:
- Recidivism Velocity: Ratio of patients with >= 3 prior episodes (NUMPRG >= 3)
- Premature Attrition: Rate of AMA (Against Medical Advice) / Dropout discharges
- Care-Retention Elasticity: Length of stay (LOS) vs prior episodes by primary payer (Commercial vs Medicaid)
"""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PAYER_MAP = {
    1: "Self-Pay",
    2: "Private / Commercial Insurance",
    3: "Medicare",
    4: "Medicaid",
    5: "Other Government",
}

DISCHARGE_REASON_MAP = {
    1: "Completed Treatment",
    2: "Dropped Out / Left AMA",
    3: "Terminated by Facility",
    4: "Transferred to Another Facility",
    5: "Incarcerated",
    6: "Death",
    7: "Other",
}


class RevolvingDoorAnalyzer:
    """Quantitative evaluation of treatment cycle dynamics."""

    @staticmethod
    def calculate_recidivism_by_payer(df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes recidivism and dropout rates segmented by payment source.
        Expects columns: 'primpay', 'reason', 'numprg', 'los'.
        """
        valid_df = df[df["primpay"].isin(PAYER_MAP.keys())].copy()
        valid_df["payer_label"] = valid_df["primpay"].map(PAYER_MAP)
        valid_df["is_dropout_ama"] = (valid_df["reason"] == 2).astype(int)
        valid_df["is_high_recidivism"] = (valid_df["numprg"] >= 3).astype(int)

        summary = valid_df.groupby("payer_label").agg(
            total_episodes=("reason", "count"),
            dropout_rate_pct=("is_dropout_ama", lambda x: np.round(x.mean() * 100, 2)),
            high_recidivism_rate_pct=("is_high_recidivism", lambda x: np.round(x.mean() * 100, 2)),
            avg_los_days=("los", lambda x: np.round(x.mean(), 1)),
            median_los_days=("los", "median"),
        ).reset_index()

        return summary.sort_values(by="total_episodes", ascending=False)

    @staticmethod
    def calculate_revolving_door_index(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates aggregate index measuring systemic revolving door severity.
        High RDI (> 30%) indicates an extraction cycle where facilities discharge
        patients rapidly without achieving completion, prompting repeated admissions.
        """
        total = len(df)
        if total == 0:
            return {"total": 0, "revolving_door_index": 0.0}

        high_prior = (df["numprg"] >= 3).sum()
        dropouts = (df["reason"] == 2).sum()
        rdi = (high_prior / total) * 100

        return {
            "total_episodes": total,
            "episodes_with_3plus_prior_stays": int(high_prior),
            "revolving_door_index_pct": round(rdi, 2),
            "total_dropouts_ama": int(dropouts),
            "dropout_rate_pct": round((dropouts / total) * 100, 2),
        }

