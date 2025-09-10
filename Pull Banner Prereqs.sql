SELECT DISTINCT
    scbcrse_subj_code                                   AS subject_code,
    scbcrse_crse_numb                                   AS course_number,
    scbcrse_subj_code || '_' || scbcrse_crse_numb       AS course_id,
    scrrare_area                                        AS area_code,
    smracaa_set                                         AS pre_req_area_set,
    smracaa_subset                                      AS pre_req_area_subset,
    smracaa_rule                                        AS pre_req_area_rule,
    smracaa_subj_code                                   AS pre_req_subject_code,
    smracaa_crse_numb_low                               AS pre_req_course_number,
    smracaa_grde_code_min                               AS min_grade,
    smracaa_tesc_code                                   AS test_code,
    smracaa_min_value                                   AS test_score,
    smracaa_concurrency_ind                             AS allow_concurrency

FROM scbcrse
LEFT JOIN scrrare ON scbcrse_subj_code = scrrare_subj_code
    AND scbcrse_crse_numb = scrrare_crse_numb
    AND scrrare_term_code_effective = (
        SELECT MAX(b.scrrare_term_code_effective)
        FROM scrrare b
        WHERE scrrare.scrrare_subj_code = b.scrrare_subj_code
            AND scrrare.scrrare_crse_numb = b.scrrare_crse_numb
    )
    
LEFT JOIN smracaa ON scrrare_area = smracaa_area
    AND smracaa_term_code_eff = (
        SELECT MAX(c.smracaa_term_code_eff)
        FROM smracaa c
        WHERE smracaa.smracaa_area = c.smracaa_area
    )

WHERE scbcrse_eff_term = (
    SELECT MAX(a.scbcrse_eff_term)
    FROM scbcrse a
    WHERE scbcrse.scbcrse_subj_code = a.scbcrse_subj_code
        AND scbcrse.scbcrse_crse_numb = a.scbcrse_crse_numb
)
    AND scrrare_area IS NOT NULL

ORDER BY scbcrse_subj_code, scbcrse_crse_numb ASC;