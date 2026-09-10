# Druggie_buggie: Operating Protocols & Engineering Standards

## 1. Project Mission & Forensic Mandate
This project investigates the **Rehabilitation Industrial Complex**, tracking capital extraction across residential detox, intensive outpatient (IOP), sober living networks, and clinical laboratories. The investigation focuses primarily on:
- **California** (with deep-dive municipal analysis in Orange County: Costa Mesa, Newport Beach, Huntington Beach, San Clemente, Laguna Beach, Dana Point, and Santa Ana).
- **Oregon** (evaluating public Measure 110 grant disbursals vs private treatment capacity).

We examine three structural dynamics:
1. **The Revolving Door**: Patient churn, high readmission frequency (`NUMPRG`), and premature dropouts (`REASON = AMA`).
2. **Capital Extraction vs. Patient Care**: Out-of-network pricing arbitrage, urine drug screening (UDS) upcoding (CPT 80305-80307, G0480-G0483), and high executive overhead vs bedside nursing FTEs.
3. **Corporate & Real Estate Layering**: Sober living real estate networks funneled to clinical outpatient centers under separate LLCs/MSOs.

---

## 2. GitHub & Version Control Protocols (Owned by Assistant)
Referencing conventions from the neighboring `Portfolio` repository:

### A. Ownership & Proactive Git Cadence
- The assistant is directly responsible for maintaining repository hygiene.
- Commit checkpoints occur at every meaningful transition (data harvester built, schema created, transformation tested, analysis completed).
- Commit messages follow strict imperative style:
  - `Initialize project protocols and repository scaffold`
  - `Implement SAMHSA TEDS-D Bronze ingestion pipeline`
  - `Add DHCS facility entity resolution and GIS normalizer`
  - `Create forensic billing markup mart in BigQuery Gold`

### B. Hygiene & Secrets Protection
- Under no circumstances may raw bulk data files (`*.csv`, `*.parquet`, `*.zip`), database credentials, API keys, or GCP service account tokens be committed.
- All ingestion scripts must stream directly to BigQuery or store ephemeral files in gitignored `data/` or `scratch/` directories.

---

## 3. Data Architecture & BigQuery Lakehouse Design
- **Cloud Project**: `db1b-1`
- **GCP Region**: `us-west1` (matching Portfolio / Cloud Run infrastructure)
- **Dataset Layers**:
  - `rehab_bronze`: Raw, append-only landing tables storing source JSON/CSV payloads, file hashes, and ingestion timestamps.
  - `rehab_silver`: Cleaned, typed, deduplicated, and entity-resolved relational tables (e.g. `dim_facilities`, `dim_providers`, `fct_treatment_episodes`).
  - `rehab_gold`: Analytical and forensic marts ready for visualization, statistical testing, and investigative reporting.

---

## 4. Master Linkage Keys (The Forensic Rosetta Stone)
To connect patient outcomes, billing data, facility inspections, and corporate ownership:
1. **Type 1 NPI (Individual)**: Clinical directors, prescribing physicians, lab medical directors.
2. **Type 2 NPI (Organization)**: Operating clinical facilities, billing entities.
3. **State License / Certification Number**: CA DHCS license number, OR OHA license number.
4. **Standardized Physical Address / Parcel Number**: Linking unlicensed recovery residences to licensed outpatient clinics.
5. **EIN (Employer Identification Number)**: Linking state business entities to IRS Form 990 non-profit returns.
