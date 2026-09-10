-- ==============================================================================
-- Mart: rehab_gold.mart_revolving_door_attrition
-- Description: Aggregate metrics tracking recidivism velocity, dropouts (AMA),
--              and average length of stay across payment sources and states.
-- ==============================================================================

CREATE OR REPLACE VIEW `db1b-1.rehab_gold.mart_revolving_door_attrition` AS
SELECT
    discharge_year,
    CASE 
        WHEN stfips = 6 THEN 'California'
        WHEN stfips = 41 THEN 'Oregon'
        ELSE 'Other'
    END AS state_name,
    CASE 
        WHEN primpay = 1 THEN 'Self-pay'
        WHEN primpay = 2 THEN 'Blue Cross/Blue Shield or Commercial'
        WHEN primpay = 3 THEN 'Medicare'
        WHEN primpay = 4 THEN 'Medicaid'
        WHEN primpay = 5 THEN 'Other government'
        ELSE 'Unknown / Other'
    END AS primary_payment_source,
    CASE 
        WHEN services IN (1, 2) THEN 'Detoxification (Inpatient/Hospital)'
        WHEN services IN (3, 4, 5) THEN 'Rehabilitation / Residential'
        WHEN services IN (6, 7, 8) THEN 'Ambulatory / Outpatient'
        ELSE 'Other Setting'
    END AS service_setting_group,
    COUNT(1) AS total_discharges,
    COUNTIF(reason = 1) AS count_completed_treatment,
    COUNTIF(reason = 2) AS count_dropped_out_or_ama,
    COUNTIF(numprg >= 3) AS count_high_recidivism_3plus_prior,
    ROUND(SAFE_DIVIDE(COUNTIF(reason = 2), COUNT(1)) * 100, 2) AS dropout_rate_pct,
    ROUND(SAFE_DIVIDE(COUNTIF(numprg >= 3), COUNT(1)) * 100, 2) AS revolving_door_rate_pct,
    ROUND(AVG(los), 1) AS avg_length_of_stay_days
FROM `db1b-1.rehab_bronze.raw_samhsa_teds_discharges`
WHERE stfips IN (6, 41)
GROUP BY 1, 2, 3, 4;

