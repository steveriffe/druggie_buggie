# Druggie_buggie 🔬💉🏛️

**Following the Money in the Rehabilitation Industry**

A forensic data engineering and investigative analysis platform tracking capital flows, recidivism ("the revolving door"), corporate entity webs, and clinical care allocation across the addiction treatment industry.

---

## Geographic & Municipal Scope
- **California**: Statewide treatment facility licensing, disciplinary enforcement, Medicaid/commercial claims, and hospital financial disclosures.
- **Orange County ("Rehab Riviera")**: Focused municipal investigation across **Costa Mesa, Newport Beach, Huntington Beach, San Clemente, Laguna Beach, Dana Point, and Santa Ana**, contrasting licensed facility capacity with congregate recovery/sober living residences.
- **Oregon**: Tracking state behavioral health licensing, public Measure 110 grant allocations, and All Payer All Claims (APAC) benchmarks.

---

## Core Investigation Pillars
1. **The Revolving Door**: Measuring readmission velocity (`NUMPRG`), length of stay (`LOS`), and early dropouts (`REASON = AMA`) using SAMHSA TEDS-D microdata.
2. **Capital Extraction vs. Patient Care**: Analyzing out-of-network facility billing, urine drug testing upcoding (CPT 80305–80307, G0480–G0483), and nursing hours vs executive compensation.
3. **Corporate Entity Networks**: Resolving links between unlicensed sober living properties, licensed clinical outpatient facilities, holding companies, and private equity ownership.

---

## Quickstart & Protocols
See [PROTOCOL.md](PROTOCOL.md) for data architecture standards, BigQuery conventions (`db1b-1`, region `us-west1`), and git commit protocols.
See [docs/RESEARCH_DATA_ACCESS_PATHWAY.md](docs/RESEARCH_DATA_ACCESS_PATHWAY.md) for the roadmap to apply for restricted APCD datasets (California HPD and Oregon APAC).

### Dependencies
```bash
pip install -r requirements.txt
```
