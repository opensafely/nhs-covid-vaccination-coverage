# Import functions

from cohortextractor import (
    StudyDefinition,
    patients,
    codelist_from_csv,
    codelist,
    filter_codes_by_category,
    combine_codelists,
)

# Import codelists

from codelists import *
from study_definition_delivery_u16_common import (
    common_variables,
    campaign_start,
    index_date,
)

specific_atrisk_date = "2020-07-01"

# Specify study definition

study = StudyDefinition(
    index_date=index_date,
    nulldate=patients.fixed_value("1902-01-01"),
    # ETHNICITY IN 16 CATEGORIES
    ethnicity_16=patients.with_these_clinical_events(
        ethnicity_codes_16,
        returning="category",
        find_last_match_in_period=True,
        include_date_of_match=False,
        return_expectations={
            "category": {
                "ratios": {
                    "1": 0.0625,
                    "2": 0.0625,
                    "3": 0.0625,
                    "4": 0.0625,
                    "5": 0.0625,
                    "6": 0.0625,
                    "7": 0.0625,
                    "8": 0.0625,
                    "9": 0.0625,
                    "10": 0.0625,
                    "11": 0.0625,
                    "12": 0.0625,
                    "13": 0.0625,
                    "14": 0.0625,
                    "15": 0.0625,
                    "16": 0.0625,
                }
            },
            "incidence": 0.75,
        },
    ),
    # ETHNICITY IN 6 CATEGORIES
    ethnicity=patients.with_these_clinical_events(
        ethnicity_codes,
        returning="category",
        find_last_match_in_period=True,
        include_date_of_match=False,
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.75,
        },
    ),
    # fill missing ethnicity from SUS
    ethnicity_6_sus=patients.with_ethnicity_from_sus(
        returning="group_6",
        use_most_frequent_code=True,
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.4,
        },
    ),
    ethnicity_16_sus=patients.with_ethnicity_from_sus(
        returning="group_16",
        use_most_frequent_code=True,
        return_expectations={
            "category": {
                "ratios": {
                    "1": 0.0625,
                    "2": 0.0625,
                    "3": 0.0625,
                    "4": 0.0625,
                    "5": 0.0625,
                    "6": 0.0625,
                    "7": 0.0625,
                    "8": 0.0625,
                    "9": 0.0625,
                    "10": 0.0625,
                    "11": 0.0625,
                    "12": 0.0625,
                    "13": 0.0625,
                    "14": 0.0625,
                    "15": 0.0625,
                    "16": 0.0625,
                }
            },
            "incidence": 0.4,
        },
    ),
    ### Generating ATRISK_GROUP (v1.5.3 of PRIMIS specification)
    ### Code borrowed and amended from
    ### https://github.com/opensafely/vaccine-effectiveness-in-kids/commit/4569b89213b6bb0927e2f44e1c55ebab28576bcc
    # housebound = patients.satisfying(
    #     """housebound_date
    #     AND NOT no_longer_housebound
    #     AND NOT moved_into_care_home
    #     """,
    #     housebound_date=patients.with_these_clinical_events(
    #     housebound_codes,
    #     on_or_before="index_date - 1 day",
    #     find_last_match_in_period = True,
    #     returning="date",
    #     date_format="YYYY-MM-DD",
    #     ),
    #     no_longer_housebound=patients.with_these_clinical_events(
    #     no_longer_housebound_codes,
    #     between=["housebound_date", "index_date - 1 day"],
    #     ),
    #     moved_into_care_home=patients.with_these_clinical_events(
    #     care_home_snomed_codes,
    #     between=["housebound_date", "index_date - 1 day"],
    #     ),
    # ),
    child_atrisk=patients.satisfying(
        """
        ATRISK_GROUP
        OR
        HHLD_IMDEF
        OR
        PREG1_GROUP
        """,
        HHLD_IMDEF=patients.with_these_clinical_events(
            hhld_imdef_cod,
            on_or_before="index_date",
        ),
        ATRISK_GROUP=patients.satisfying(
            """
            IMMUNOGROUP
            OR
            CKD_GROUP
            OR
            RESP_GROUP
            OR
            DIAB_GROUP 
            OR
            CLD
            OR
            CNS_GROUP
            OR
            CHD_COV
            OR
            SPLN_COV
            OR
            LEARNDIS
            OR
            SEVMENT_GROUP
            """,
            ##### Patients with Immunosuppression
            IMMUNOGROUP=patients.satisfying(
                """
                IMMDX
                OR
                IMMRX
                OR
                DXT_CHEMO
                """,
                ###  any immunosuppressant Read code is recorded
                IMMDX=patients.with_these_clinical_events(
                    immdx_cov_cod,
                    find_last_match_in_period=True,
                    on_or_before="index_date",
                ),
                ### any Immunosuppression medication codes is recorded
                IMMRX=patients.with_these_clinical_events(
                    immrx_cod,
                    find_last_match_in_period=True,
                    between=[specific_atrisk_date, "index_date"],
                ),
                ### Receiving chemotherapy or radiotherapy
                DXT_CHEMO=patients.with_these_clinical_events(
                    dxt_chemo_cod,
                    find_last_match_in_period=True,
                    between=["index_date - 6 months", "index_date"],
                ),
            ),
            # Patients with Chronic Kidney Disease
            # as per official COVID-19 vaccine reporting specification
            # IF CKD_COV_DAT > NULL (diagnoses) | Select | Next
            # IF CKD15_DAT = NULL  (No stages)   | Reject | Next
            # IF CKD35_DAT>=CKD15_DAT            | Select | Reject
            # (i.e. any diagnostic code, or most recent stage recorded >=3)
            CKD_GROUP=patients.satisfying(
                """
                CKD_COV
                OR
                (
                CKD15_DAT
                AND
                CKD15_DAT > nulldate
                AND
                CKD35_DAT
                AND
                CKD35_DAT > nulldate
                AND
                CKD15
                AND
                CKD35_DAT >= CKD15_DAT 
                )
                """,
                ### Chronic kidney disease diagnostic codes
                CKD_COV=patients.with_these_clinical_events(
                    ckd_cov_cod,
                    find_first_match_in_period=True,
                    on_or_before="index_date",
                ),
                ### Chronic kidney disease codes - all stages
                CKD15=patients.with_these_clinical_events(
                    ckd15_cod,
                    find_last_match_in_period=True,
                    on_or_before="index_date",
                ),
                ### date of Chronic kidney disease codes-stages 3 – 5
                CKD35_DAT=patients.with_these_clinical_events(
                    ckd35_cod,
                    returning="date",
                    find_last_match_in_period=True,
                    date_format="YYYY-MM-DD",
                    on_or_before="index_date",
                ),
                ### date of Chronic kidney disease codes - all stages
                CKD15_DAT=patients.with_these_clinical_events(
                    ckd15_cod,
                    returning="date",
                    date_format="YYYY-MM-DD",
                    on_or_before="index_date",
                    find_last_match_in_period=True,
                ),
            ),
            ### Patients who have Chronic Respiratory Disease
            RESP_GROUP=patients.satisfying(
                """
                AST_GROUP
                OR
                RESP_COV 
                """,
                ### Patients with Asthma
                AST_GROUP=patients.satisfying(
                    """
                ASTADM
                OR
                (
                AST
                AND
                ASTRXM1
                AND
                ASTRXM2 > 1
                )
                """,
                    ### Asthma Admission codes
                    ASTADM=patients.with_these_clinical_events(
                        astadm_cod,
                        find_last_match_in_period=True,
                        between=["index_date - 730 days", "index_date"],
                    ),
                    ### Asthma Diagnosis code
                    AST=patients.with_these_clinical_events(
                        ast_cod,
                        find_first_match_in_period=True,
                        on_or_before="index_date",
                    ),
                    ### Asthma - inhalers in last 12 months
                    ASTRXM1=patients.with_these_medications(
                        astrxm1_cod,
                        returning="binary_flag",
                        between=["index_date - 365 days", "index_date"],
                    ),
                    ### Asthma - systemic oral steroid prescription codes in last 24 months
                    ASTRXM2=patients.with_these_medications(
                        astrxm2_cod,
                        returning="number_of_matches_in_period",
                        between=["index_date - 730 days", "index_date"],
                    ),
                ),
                ### Chronic Respiratory Disease
                RESP_COV=patients.with_these_clinical_events(
                    resp_cov_cod,
                    find_first_match_in_period=True,
                    returning="binary_flag",
                    on_or_before="index_date",
                ),
            ),
            ### Patients with Diabetes
            DIAB_GROUP=patients.satisfying(
                """
                (
                    DIAB_DAT
                    AND
                    DIAB_DAT > nulldate
                    AND
                    DIAB_DAT > DMRES_DAT
                )
                OR
                ADDIS
                OR
                GDIAB_GROUP
                """,
                ### Date any Diabetes diagnosis Read code is recorded
                DIAB_DAT=patients.with_these_clinical_events(
                    diab_cod,
                    returning="date",
                    find_last_match_in_period=True,
                    on_or_before="index_date",
                    date_format="YYYY-MM-DD",
                ),
                ### Date of Diabetes resolved codes
                DMRES_DAT=patients.with_these_clinical_events(
                    dmres_cod,
                    returning="date",
                    find_last_match_in_period=True,
                    on_or_before="index_date",
                    date_format="YYYY-MM-DD",
                ),
                ### Addison’s disease & Pan-hypopituitary diagnosis codes
                ADDIS=patients.with_these_clinical_events(
                    addis_cod,
                    find_last_match_in_period=True,
                    returning="binary_flag",
                    on_or_before="index_date",
                ),
                ### Patients who are currently pregnant with gestational diabetes
                GDIAB_GROUP=patients.satisfying(
                    """
                GDIAB
                AND
                PREG1_GROUP
                """,
                    ### Gestational Diabetes diagnosis codes
                    GDIAB=patients.with_these_clinical_events(
                        gdiab_cod,
                        find_last_match_in_period=True,
                        returning="binary_flag",
                        between=["index_date - 254 days", "index_date"],
                    ),
                    ### Patients who are currently pregnant
                    PREG1_GROUP=patients.satisfying(
                        """
                    PREG
                    AND
                    PREG_DAT
                    AND
                    PREGDEL_DAT < PREG_DAT
                    """,
                        ### Pregnancy codes recorded in the 8.5 months before the audit run date
                        PREG=patients.with_these_clinical_events(
                            preg_cod,
                            returning="binary_flag",
                            between=["index_date - 254 days", "index_date"],
                        ),
                        ### Pregnancy or Delivery codes recorded in the 8.5 months before audit run date
                        PREGDEL_DAT=patients.with_these_clinical_events(
                            pregdel_cod,
                            returning="date",
                            find_last_match_in_period=True,
                            between=["index_date - 254 days", "index_date"],
                            date_format="YYYY-MM-DD",
                        ),
                        ### Date of pregnancy codes recorded in the 8.5 months before audit run date
                        PREG_DAT=patients.with_these_clinical_events(
                            preg_cod,
                            returning="date",
                            find_last_match_in_period=True,
                            between=["index_date - 254 days", "index_date"],
                            date_format="YYYY-MM-DD",
                        ),
                    ),
                ),
            ),
            ### Chronic Liver disease codes
            CLD=patients.with_these_clinical_events(
                cld_cod,
                find_first_match_in_period=True,
                returning="binary_flag",
                on_or_before="index_date",
            ),
            ### Patients with CNS Disease (including Stroke/TIA)
            CNS_GROUP=patients.with_these_clinical_events(
                cns_cov_cod,
                find_first_match_in_period=True,
                returning="binary_flag",
                on_or_before="index_date",
            ),
            ### Chronic heart disease codes
            CHD_COV=patients.with_these_clinical_events(
                chd_cov_cod,
                find_first_match_in_period=True,
                returning="binary_flag",
                on_or_before="index_date",
            ),
            ### Asplenia or Dysfunction of the Spleen codes
            SPLN_COV=patients.with_these_clinical_events(
                spln_cov_cod,
                find_first_match_in_period=True,
                returning="binary_flag",
                on_or_before="index_date",
            ),
            ### Wider Learning Disability
            LEARNDIS=patients.with_these_clinical_events(
                learndis_cod,
                find_last_match_in_period=True,
                returning="binary_flag",
                on_or_before="index_date",
            ),
            ### Patients with Severe Mental Health
            SEVMENT_GROUP=patients.satisfying(
                """
            SEV_MENTAL_DAT
            AND
            SEV_MENTAL_DAT > nulldate
            AND
            SEV_MENTAL_DAT > SMHRES_DAT
            """,
                ### date of Severe Mental Illness codes
                SEV_MENTAL_DAT=patients.with_these_clinical_events(
                    sev_mental_cod,
                    returning="date",
                    find_last_match_in_period=True,
                    on_or_before="index_date",
                    date_format="YYYY-MM-DD",
                ),
                ### date of Remission codes relating to Severe Mental Illness
                SMHRES_DAT=patients.with_these_clinical_events(
                    smhres_cod,
                    returning="date",
                    find_last_match_in_period=True,
                    on_or_before="index_date",
                    date_format="YYYY-MM-DD",
                ),
            ),
        ),
    ),
    ###############################################################################
    # COVID VACCINATION
    ###############################################################################
    # any COVID vaccination (first dose)
    covid_vacc_date=patients.with_tpp_vaccination_record(
        target_disease_matches="SARS-2 CORONAVIRUS",
        on_or_after="2021-08-04",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-08-04",  # JCVI announced recommendation for 12+ high risk children on 4/8/21
                "latest": index_date,
            },
            "incidence": 0.9,
        },
    ),
    # SECOND DOSE COVID VACCINATION - this varies depending on the cohort
    # - high risk should have a gap of 8 weeks (or 56 days)
    # - everyone else should have a gap of 12 weeks (or 84 days)
    # We will therefore use 7 weeks (to accommodate both cohorts and allow
    # for early vaccination).
    covid_vacc_second_dose_date=patients.with_tpp_vaccination_record(
        target_disease_matches="SARS-2 CORONAVIRUS",
        on_or_after="covid_vacc_date + 49 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-09-22",  # 7 weeks after 4/8/21
                "latest": index_date,
            },
            "incidence": 0.8,
        },
    ),
    # BOOSTER (3rd) DOSE COVID VACCINATION
    # Advice exists for high risk adolescents (12-15yo) for no less than 3 months
    # after primary course; advice for all other groups is still under review.
    # HOWEVER, if we implement something like 77 days here, we will miss third doses in the primary
    # course for immunocompromised adolescents and children, so we are setting this to be one
    # week less than 8 weeks to capture both third doses and boosters.
    covid_vacc_third_dose_date=patients.with_tpp_vaccination_record(
        target_disease_matches="SARS-2 CORONAVIRUS",
        on_or_after="covid_vacc_second_dose_date + 49 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-11-10",  # 7 weeks after 22/9/2021 (14 weeks after 4/8/21)
                "latest": index_date,
            },
            "incidence": 0.1,
        },
    ),
    # COVID VACCINATION - Pfizer BioNTech
    covid_vacc_pfizerA_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Comirnaty 30micrograms/0.3ml dose conc for susp for inj MDV (Pfizer)",
        on_or_after="2021-08-04",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                # JCVI announced recommendation for 12+ high risk children on 4/8/21
                "earliest": "2021-08-04",
                "latest": index_date,
            },
            "incidence": 0.7,
        },
    ),
    ### One vaccine approved for use in children (5-11)
    covid_vacc_pfizerC_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Comirnaty Children 5-11yrs 10mcg/0.2ml dose conc for disp for inj MDV (Pfizer)",
        on_or_after="2021-12-22",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-12-22",  # vaccine approved on 22/12/2021
                "latest": index_date,
            },
            "incidence": 0.7,
        },
    ),
    # COVID VACCINATION - Oxford AZ
    covid_vacc_oxford_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 Vaccine Vaxzevria 0.5ml inj multidose vials (AstraZeneca)",
        on_or_after="2021-08-04",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                # JCVI announced recommendation for 12+ high risk children on 4/8/21
                "earliest": "2021-08-04",
                "latest": index_date,
            },
            "incidence": 0.7,
        },
    ),
    # COVID VACCINATION - Moderna
    covid_vacc_moderna_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Spikevax (nucleoside modified) 0.1mg/0.5mL dose disp for inj MDV (Moderna)",
        on_or_after="2021-08-04",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                # JCVI announced recommendation for 12+ high risk children on 4/8/21
                "earliest": "2021-08-04",
                "latest": index_date,
            },
            "incidence": 0.4,
        },
    ),
    ## BRAND OF THIRD/BOOSTER DOSES
    # BOOSTER (3rd) DOSE COVID VACCINATION - Pfizer child
    covid_vacc_third_dose_pfizerC_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Comirnaty Children 5-11yrs 10mcg/0.2ml dose conc for disp for inj MDV (Pfizer)",
        on_or_after="covid_vacc_second_dose_date + 49 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                # 7 weeks after 22/9/2021 (14 weeks after 4/8/21)
                "earliest": "2021-11-10",
                "latest": index_date,
            },
            "incidence": 0.25,
        },
    ),
    # BOOSTER (3rd) DOSE COVID VACCINATION - Pfizer adult
    covid_vacc_third_dose_pfizerA_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Comirnaty 30micrograms/0.3ml dose conc for susp for inj MDV (Pfizer)",
        on_or_after="covid_vacc_second_dose_date + 49 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-11-10",  # 7 weeks after 22/9/2021 (14 weeks after 4/8/21)
                "latest": index_date,
            },
            "incidence": 0.10,
        },
    ),
    # BOOSTER (3rd) DOSE COVID VACCINATION - Oxford AZ
    covid_vacc_third_dose_oxford_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 Vaccine Vaxzevria 0.5ml inj multidose vials (AstraZeneca)",
        on_or_after="covid_vacc_second_dose_date + 49 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-11-10",  # 7 weeks after 22/9/2021 (14 weeks after 4/8/21)
                "latest": index_date,
            },
            "incidence": 0.10,
        },
    ),
    # BOOSTER (3rd) DOSE COVID VACCINATION - Moderna
    covid_vacc_third_dose_moderna_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Spikevax (nucleoside modified) 0.1mg/0.5mL dose disp for inj MDV (Moderna)",
        on_or_after="covid_vacc_second_dose_date + 49 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-11-10",  # 7 weeks after 22/9/2021 (14 weeks after 4/8/21)
                "latest": index_date,
            },
            "incidence": 0.25,
        },
    ),
    **common_variables
)
