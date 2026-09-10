# Research Data Set Application Pathway & Strategy

This document establishes the step-by-step roadmap for requesting and acquiring restricted, longitudinal healthcare microdata to expand our initial open-data findings into empirical, claims-level research.

---

## Target Restricted Repositories

### 1. California Health Care Payments Database (HPD)
- **Governing Body**: California Department of Health Care Access and Information (HCAI).
- **Data Scope**: Longitudinal claims, encounters, and payment microdata covering commercial insurance, Medi-Cal Managed Care, and Medicare Advantage across California.
- **Key Fields**: Actual negotiated paid amounts vs billed charges, patient out-of-pocket costs, revenue codes (0160, 1002, 0905, 0906), service dates, and unique encrypted member IDs.
- **Application Path**:
  - Research application submitted to the **HPD Data Release Committee (DRC)**.
  - Requires Data Use Agreement (DUA), Data Management Plan (DMP) complying with HIPAA and California state privacy statutes, and IRB approval / exemption.

### 2. Oregon All Payer All Claims (APAC) System
- **Governing Body**: Oregon Health Authority (OHA) Office of Health Analytics under ORS 442.373.
- **Data Scope**: Approximately 92% of all insured Oregonians, across commercial health plans, CCOs (Medicaid), and Medicare.
- **Key Fields**: Episode-level medical and pharmacy claims, institutional revenue codes, CPT/HCPCS, provider NPIs, and cross-facility patient tracking.
- **Application Path**:
  - Submit **APAC-3 Research Application** to the OHA Data Review Committee.
  - Request link to the **Center for Health Statistics (CHS)** death certificate registry to evaluate post-discharge mortality and fatal overdose rates following SUD discharge.

---

## Strategy: Using Foundational Open-Data Research to Secure Access
State data release committees evaluate data requests based on **public interest, empirical methodology, and data necessity**. We will leverage our open-data pipeline to build an airtight research proposal:

1. **Demonstrate Preliminary Evidence**:
   - Use our SAMHSA TEDS-D findings (`NUMPRG` readmission spikes, high AMA dropouts) as baseline evidence demonstrating that SUD treatment exhibits systematic recidivism.
   - Use CMS Open Payments to show documentation of financial relationships between treatment directors and high-volume toxicology labs.
2. **Formulate High-Impact Public Interest Questions**:
   - What are the true price differentials between billed charges and commercial settlements for inpatient detox vs outpatient care in Orange County?
   - What is the longitudinal mortality rate among individuals experiencing 3+ treatment episodes within a 24-month window?
3. **Institutional Review & DUA Readiness**:
   - Prepare secure cloud computing architecture (e.g. BigQuery VPC Service Controls / Customer-Managed Encryption Keys) satisfying all state-mandated security benchmarks.
