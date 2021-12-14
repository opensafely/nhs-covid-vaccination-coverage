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
from study_definition_delivery_common import common_variables, campaign_start, index_date
    
# Specify study definition

study = StudyDefinition(
    index_date = index_date,
    

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
    ethnicity_6_sus = patients.with_ethnicity_from_sus(
        returning="group_6",  
        use_most_frequent_code=True,
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.4,
            },
    ),
    
    ethnicity_16_sus = patients.with_ethnicity_from_sus(
        returning="group_16",  
        use_most_frequent_code=True,
        return_expectations={
            "category": {"ratios": {"1": 0.0625,
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
                    "16": 0.0625,}},
            "incidence": 0.4,
            },
    ),

    # CLINICAL CO-MORBIDITIES WORK IN PROGRESS IN COLLABORATION WITH NHSX
    # https://github.com/opensafely/vaccine-eligibility/blob/master/analysis/study_definition.py
    chronic_cardiac_disease=patients.with_these_clinical_events(
        chronic_cardiac_disease_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    current_copd=patients.with_these_clinical_events(
        current_copd_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    # dementia
    dementia=patients.with_these_clinical_events(
        dementia_codes, 
        on_or_before=index_date,
        returning="binary_flag", 
        return_expectations={"incidence": 0.01,},
    ),
    dialysis=patients.with_these_clinical_events(
        dialysis_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    solid_organ_transplantation=patients.with_these_clinical_events(
        solid_organ_transplantation_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    chemo_or_radio=patients.with_these_clinical_events(
        chemotherapy_or_radiotherapy_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    intel_dis_incl_downs_syndrome=patients.with_these_clinical_events(
        intellectual_disability_including_downs_syndrome_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    lung_cancer=patients.with_these_clinical_events(
        lung_cancer_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    cancer_excl_lung_and_haem=patients.with_these_clinical_events(
        cancer_excluding_lung_and_haematological_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    haematological_cancer=patients.with_these_clinical_events(
        haematological_cancer_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    bone_marrow_transplant=patients.with_these_clinical_events(
        bone_marrow_transplant_codes,
        between=["index_date - 6 months", index_date],
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    # cystic_fibrosis=patients.with_these_clinical_events(
    #     cystic_fibrosis_codes,
    #     on_or_before=index_date,
    #     returning="binary_flag",
    #     return_expectations={"incidence": 0.01,},
    # ),
    # sickle_cell_disease=patients.with_these_clinical_events(
    #     sickle_cell_disease_codes,
    #     on_or_before=index_date,
    #     returning="binary_flag",
    #     return_expectations={"incidence": 0.01,},
    # ),
    # permanant_immunosuppression=patients.with_these_clinical_events(
    #     permanent_immunosuppression_codes,
    #     on_or_before=index_date,
    #     returning="binary_flag",
    #     return_expectations={"incidence": 0.01,},
    # ),
    # temporary_immunosuppression=patients.with_these_clinical_events(
    #     temporary_immunosuppression_codes,
    #     on_or_before=index_date,
    #     returning="binary_flag",
    #     return_expectations={"incidence": 0.01,},
    # ),
    #
    psychosis_schiz_bipolar=patients.with_these_clinical_events(
        psychosis_schizophrenia_bipolar_affective_disease_codes,
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),

    # https://github.com/opensafely/codelist-development/issues/4
    # asplenia=patients.with_these_clinical_events(
    #     asplenia_codes,
    #     on_or_before=index_date,
    #     returning="binary_flag",
    #     return_expectations={"incidence": 0.01,},
    # ),

    ###############################################################################
    # COVID VACCINATION
    ###############################################################################
    # any COVID vaccination (first dose)
    covid_vacc_date=patients.with_tpp_vaccination_record(
        target_disease_matches="SARS-2 CORONAVIRUS",
        on_or_after="2020-12-01",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-08",  # first vaccine administered on the 8/12
                "latest": index_date,
            },
                "incidence":0.9
        },
    ),
    # SECOND DOSE COVID VACCINATION
    covid_vacc_second_dose_date=patients.with_tpp_vaccination_record(
        target_disease_matches="SARS-2 CORONAVIRUS",
        on_or_after="covid_vacc_date + 19 days",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-29",  # first reported second dose administered on the 29/12
                "latest": index_date,
            },
                "incidence": 0.8
        },
    ),
    
    # BOOSTER (3rd) DOSE COVID VACCINATION
    ## Booster dose scehdule is 6 months from 2nd dose. However, for now, we will use an 8 week interval, 
    ## to ensure that anyone having a third dose within the primary course (immunosuppressed, from 1st Sept) 
    ## are not shown as due/missing a booster dose.
    ## however those with third doses will also eventually become eligible for booster so this may need to be revisited
    covid_vacc_third_dose_date=patients.with_tpp_vaccination_record(
        target_disease_matches="SARS-2 CORONAVIRUS",
        on_or_after="covid_vacc_second_dose_date + 56 days", 
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-09-24",  # first booster dose recorded
                "latest": index_date,
            },
                "incidence": 0.1
        },
    ),
    
    # COVID VACCINATION - Pfizer BioNTech
    covid_vacc_pfizer_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Comirnaty 30micrograms/0.3ml dose conc for susp for inj MDV (Pfizer)",
        on_or_after="2020-12-01",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-08",  # first vaccine administered on the 8/12
                "latest": index_date,},
            "incidence": 0.7
        },
    ),
    # COVID VACCINATION - Oxford AZ
    covid_vacc_oxford_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
        on_or_after="2020-12-01",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-01-04",  # first vaccine administered on the 4/1
                "latest": index_date,
            },
            "incidence": 0.7
        },
    ),

    # COVID VACCINATION - Moderna
    covid_vacc_moderna_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Spikevax (nucleoside modified) 0.1mg/0.5mL dose disp for inj MDV (Moderna)",
        on_or_after="2020-12-01",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-04-01",  # expected from early april
                "latest": index_date,
            },
            "incidence": 0.4
        },
    ),

    
    ## BRAND OF THIRD/BOOSTER DOSES
    # BOOSTER (3rd) DOSE COVID VACCINATION - Pfizer
    covid_vacc_third_dose_pfizer_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Comirnaty 30micrograms/0.3ml dose conc for susp for inj MDV (Pfizer)",
        on_or_after="covid_vacc_second_dose_date + 56 days", 
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-09-24",  # first booster dose recorded
                "latest": index_date,
            },
                "incidence": 0.25
        },
    ),
    
    # BOOSTER (3rd) DOSE COVID VACCINATION - Oxford AZ
    covid_vacc_third_dose_oxford_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV",
        on_or_after="covid_vacc_second_dose_date + 56 days", 
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-09-24",  # first booster dose recorded
                "latest": index_date,
            },
                "incidence": 0.10
        },
    ),
    
    # BOOSTER (3rd) DOSE COVID VACCINATION - Moderna
    covid_vacc_third_dose_moderna_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vaccine Spikevax (nucleoside modified) 0.1mg/0.5mL dose disp for inj MDV (Moderna)",
        on_or_after="covid_vacc_second_dose_date + 56 days", 
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2021-09-24",  # first booster dose recorded
                "latest": index_date,
            },
                "incidence": 0.25
        },
    ),
    
    **common_variables
)
