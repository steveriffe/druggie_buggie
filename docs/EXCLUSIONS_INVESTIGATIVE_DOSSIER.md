# Investigative Dossier: Federal Exclusions & Fraud Networks in the "Rehab Riviera"

**Geographic Scope**: Coastal Orange County (Dana Point, Costa Mesa, Newport Beach, Huntington Beach, San Clemente, Laguna Beach, San Juan Capistrano, Santa Ana)  
**Primary Source**: HHS-OIG List of Excluded Individuals and Entities (LEIE), cross-referenced with BigQuery Lakehouse (`db1b-1.rehab_bronze.raw_hhs_oig_exclusions` & `db1b-1.rehab_silver.dim_facilities`).

---

## Executive Summary of Exclusion Density
Across the 8 target coastal Orange County municipalities, our BigQuery query identified **188 federally excluded entities and individuals**:
- **Santa Ana**: 56
- **Huntington Beach**: 42
- **Costa Mesa**: 30
- **Newport Beach**: 28
- **San Clemente**: 13
- **Laguna Beach**: 9
- **Dana Point**: 5
- **San Juan Capistrano**: 5

### Statutory Breakdown
- **46.3% (87 cases) under 1128(b)(4)**: Mandatory exclusion triggered by revocation or suspension of a medical or professional healthcare license by the California Medical Board or nursing board.
- **19.7% (37 cases) under 1128(a)(1)**: Felony conviction for Medicare, Medi-Cal, or private healthcare fraud, kickbacks, or patient brokering.
- **7.4% (14 cases) under 1128(a)(3)**: Felony conviction for fraud, theft, embezzlement, or breach of financial fiduciary responsibility in healthcare.
- **4.8% (9 cases) under 1128(a)(2)**: Criminal conviction for patient abuse or neglect.
- **2.1% (4 cases) under 1128(a)(4)**: Felony conviction for unlawful manufacture, distribution, or dispensing of controlled substances.

---

## High-Priority Investigative Targets: The Functional Segments

### 1. Directly Excluded Addiction Treatment Center
| Entity Name | Location | Primary Specialty | Exclusion Statute | Exclusion Date | Master Linkage Key (NPI) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SATORI RECOVERY CENTER, LLC** | 2260 Park Ave, **Laguna Beach**, CA | Substance Abuse Rehab | **1128(a)(1)** (Felony Healthcare Fraud / Kickbacks) | 2025-08-20 | **NPI: 1831545078** |

*Investigative Significance*: Satori Recovery Center operated as a private addiction treatment center in Laguna Beach. Its federal exclusion under 1128(a)(1) indicates a formal criminal conviction relating to fraudulent healthcare billing or illegal kickbacks.

---

### 2. The Marketing & "Body Brokering" Pipeline (Recruiters & Cappers)
Federal and state investigations have repeatedly shown that commercial addiction treatment in Southern California relies on aggressive patient recruitment pipelines ("body brokering"). The HHS-OIG database confirms explicit exclusions in this exact occupational category:

| Individual Name | City | Registered Address | Occupation / Specialty | Exclusion Authority | Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PERSEVERANDA GIESEKE** | **Costa Mesa** | 1016 El Camino Dr, #A | **RECRUITER/CAPPER** | **1128(a)(1)** (Felony Kickbacks) | 2019-05-20 |
| **JENNIFER LICHT** | **Huntington Beach** | 19446 Woodlands Dr | **RECRUITER/CAPPER** | **1128(a)(1)** (Felony Kickbacks) | 2018-04-19 |
| **JOHN GARBINO** | **Dana Point** | 25531 Goldenspring Dr | **BUS OWNER/EXEC - MARKETING FIRM** | **1128(a)(3)** (Felony Fraud / Embezzlement) | 2023-06-20 |
| **ROBERT LAMATTINA** | **San Juan Capistrano** | 34101 Via California, Unit 27 | **BUS OWNER/EXEC - MARKETING FIRM** | **1128(a)(3)** (Felony Financial Misconduct) | 2024-03-20 |

*Investigative Significance*: The presence of individuals excluded under felony fraud authorities classified explicitly as "Recruiter/Capper" and "Marketing Firm" in Costa Mesa, Huntington Beach, and Dana Point highlights the geographic concentration of lead-generation and referral schemes funneled into Orange County residential treatment centers.

---

### 3. Toxicology Laboratory & Diagnostic Testing Entities
High-volume urine drug screening (UDS) represents the highest-margin revenue stream in out-of-network addiction treatment, with individual residential and IOP stays generating up to \$50,000–\$100,000 in urinalysis billing alone:

| Individual / Entity | City | Registered Address | Facility / Industry Type | Exclusion Authority | Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IMRAN SHAMS** | **Huntington Beach** | 17682 Cameron St, #F | **CLINICAL LABORATORY OWNER/OPERATOR** | **1128(a)(1)** | 2004-08-19 |
| **SARA SOULATI** | **Newport Beach** | 328 Vista Trucha | **LAB / DIAGNOSTIC TESTING OWNER** | **1128(a)(1)** | 2026-05-20 |

---

### 4. Dana Point Micro-Cluster: Facility Co-Location & Proximity
In **Dana Point**, 5 federal exclusions were identified. Spatial and address matching against our licensed facility database (`rehab_silver.dim_facilities`) reveals direct geographic clustering:

1. **Dr. Kevin London, MD (24722 El Camino Capistrano, Dana Point)**:
   - *Exclusion*: 1128(b)(4) (Medical License Revocation).
   - *Proximity Link*: Located at **24722 El Camino Capistrano**, directly adjacent to licensed residential detox facility **Laguna Shores Behavioral Health LLC (24662 El Camino Capistrano)**.
2. **Dr. John Hatherley, MD (24040 Camino Del Avion, Apt 28, Dana Point)**:
   - *Exclusion*: 1128(b)(4) (Internal Medicine License Revocation).
3. **John Garbino (25531 Goldenspring Dr, Dana Point)**:
   - *Exclusion*: 1128(a)(3) (Healthcare Marketing Executive felony fraud).
