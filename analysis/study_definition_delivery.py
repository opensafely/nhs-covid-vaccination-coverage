# Import functions

from cohortextractor import (
    StudyDefinition,
    patients,
    codelist_from_csv,
    codelist,
    filter_codes_by_category,
    combine_codelists,
)

campaign_start = "2020-12-07"
latest_date = "2021-01-13" # for expectations only atm
# Import codelists

from codelists import *


# Specifiy study defeinition

study = StudyDefinition(
    # Configure the expectations framework
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": latest_date},
        "rate": "uniform",
        "incidence": 0.2,
    },
    # This line defines the study population
    population=patients.satisfying(
        """
        registered = 1
        AND
        (covid_vacc_date
        OR
        (age >=70 AND age <= 110) 
        OR
        (care_home_type))
        AND
        NOT has_died

        """
    ),
    has_follow_up=patients.registered_with_one_practice_between(
        start_date="2019-12-01",
        end_date=campaign_start,
        return_expectations={"incidence": 0.90},
    ),
    registered=patients.registered_as_of(
        campaign_start,  # day before vaccination campaign starts - discuss with team if this should be "today"
        return_expectations={"incidence": 0.98},
    ),
    has_died=patients.died_from_any_cause(
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.05},
    ),
            
            
    # Demographic information
    
    # CAREHOME STATUS
    care_home_type=patients.care_home_status_as_of(
        campaign_start,
        categorised_as={
            "PC": """
              IsPotentialCareHome
              AND LocationDoesNotRequireNursing='Y'
              AND LocationRequiresNursing='N'
            """,
            "PN": """
              IsPotentialCareHome
              AND LocationDoesNotRequireNursing='N'
              AND LocationRequiresNursing='Y'
            """,
            "PS": "IsPotentialCareHome",
            "": "DEFAULT", # use empty string 
        },
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"PC": 0.05, "PN": 0.05, "PS": 0.05, "": 0.85,},},
        },
    ),
         
    # simple care home flag
    care_home=patients.categorised_as(
            {
            1: """care_home_type""",
            0: "DEFAULT", 
        },
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {1: 0.15, 0: 0.85,},},
        },
    ),

        
    age=patients.age_as_of(
        "2021-03-31",  # PHE defined date for calulating eligibilty across all vaccination campaigns
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
            
    ageband=patients.categorised_as(
        {
            "0": "DEFAULT",
            # consider doing an under 16 age band as well to differentiate between workers and children eligble for another reason
            "0-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >= 20 AND age < 30""",
            "30-39": """ age >= 30 AND age < 40""",
            "40-49": """ age >= 40 AND age < 50""",
            "50-59": """ age >= 50 AND age < 60""",
            "60-69": """ age >= 60 AND age < 70""",
            "70-79": """ age >= 70 AND age < 80""",
            "80+": """ age >=  80 AND age < 120""",  # age eligibility currently set at 80
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0-19": 0.125,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.125,
                }
            },
        },
    ),          
    
    
    # age bands for patients not in care homes (ie living in the community)
    ageband_community=patients.categorised_as(
        {
            "care home" : "DEFAULT",
            "0-19": """ age >= 0 AND age < 20 AND NOT care_home_type""",
            "20-29": """ age >= 20 AND age < 30 AND NOT care_home_type""",
            "30-39": """ age >= 30 AND age < 40 AND NOT care_home_type""",
            "40-49": """ age >= 40 AND age < 50 AND NOT care_home_type""",
            "50-59": """ age >= 50 AND age < 60 AND NOT care_home_type""",
            "60-69": """ age >= 60 AND age < 70 AND NOT care_home_type""",
            "70-79": """ age >= 70 AND age < 80 AND NOT care_home_type""",
            "80+": """ age >=  80 AND age < 120 AND NOT care_home_type""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "care home":0.025,
                    "0-19": 0.1,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.125,
                }
            },
        },
    ),
            

    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),
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
    # practice pseudo id
    practice_id=patients.registered_practice_as_of(
        campaign_start,  # day before vaccine campaign start
        returning="pseudo_id",
        return_expectations={
            "int": {"distribution": "normal", "mean": 1000, "stddev": 100},
            "incidence": 1,
        },
    ),
    # stp is an NHS administration region based on geography
    stp=patients.registered_practice_as_of(
        campaign_start,
        returning="stp_code",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "STP1": 0.1,
                    "STP2": 0.1,
                    "STP3": 0.1,
                    "STP4": 0.1,
                    "STP5": 0.1,
                    "STP6": 0.1,
                    "STP7": 0.1,
                    "STP8": 0.1,
                    "STP9": 0.1,
                    "STP10": 0.1,
                }
            },
        },
    ),
    # NHS administrative region
    region=patients.registered_practice_as_of(
        campaign_start,
        returning="nuts1_region_name",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.2,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.1,
                    "South East": 0.2,
                },
            },
        },
    ),

    # IMD - quintile
    imd=patients.categorised_as(
        {
            "0": "DEFAULT", 
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
        },
        index_of_multiple_deprivation=patients.address_as_of(
            campaign_start,
            returning="index_of_multiple_deprivation",
            round_to_nearest=100,
        ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.05,
                    "1": 0.19,
                    "2": 0.19,
                    "3": 0.19,
                    "4": 0.19,
                    "5": 0.19,
                }
            },
        },
    ),

            
            
    # BMI
    bmi=patients.categorised_as(
        {
            "Not obese": "DEFAULT",
            "Obese I (30-34.9)": """ bmi_value >= 30 AND bmi_value < 35""",
            "Obese II (35-39.9)": """ bmi_value >= 35 AND bmi_value < 40""",
            "Obese III (40+)": """ bmi_value >= 40 AND bmi_value < 100""", 
            # set maximum to avoid any impossibly extreme values being classified as obese
        },
        bmi_value=patients.most_recent_bmi(
            on_or_after="2015-12-01",
            minimum_age_at_measurement=16
            ),
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "Not obese": 0.7,
                    "Obese I (30-34.9)": 0.1,
                    "Obese II (35-39.9)": 0.1,
                    "Obese III (40+)": 0.1,
                }
            },
        },
    ),
            
    # CLINICAL CO-MORBIDITIES WORK IN PROGRESS IN COLLABORATION WITH NHSX
    # https://github.com/opensafely/vaccine-eligibility/blob/master/analysis/study_definition.py
    chronic_cardiac_disease=patients.with_these_clinical_events(
        chronic_cardiac_disease_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    current_copd=patients.with_these_clinical_events(
        current_copd_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    # on a dmard - indicative of immunosuppression
    dmards=patients.with_these_medications(
        dmards_codes, 
        on_or_before=campaign_start,
        returning="binary_flag", 
        return_expectations={"incidence": 0.01,},
    ),
    # dementia
    dementia=patients.with_these_clinical_events(
        dementia_codes, 
        on_or_before=campaign_start,
        returning="binary_flag", 
        return_expectations={"incidence": 0.01,},
    ),
    dialysis=patients.with_these_clinical_events(
        dialysis_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    solid_organ_transplantation=patients.with_these_clinical_events(
        solid_organ_transplantation_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    chemo_or_radio=patients.with_these_clinical_events(
        chemotherapy_or_radiotherapy_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    intel_dis_incl_downs_syndrome=patients.with_these_clinical_events(
        intellectual_disability_including_downs_syndrome_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    lung_cancer=patients.with_these_clinical_events(
        lung_cancer_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    cancer_excl_lung_and_haem=patients.with_these_clinical_events(
        cancer_excluding_lung_and_haematological_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    haematological_cancer=patients.with_these_clinical_events(
        haematological_cancer_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    bone_marrow_transplant=patients.with_these_clinical_events(
        bone_marrow_transplant_codes,
        between=["2020-07-01", campaign_start],
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    cystic_fibrosis=patients.with_these_clinical_events(
        cystic_fibrosis_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    sickle_cell_disease=patients.with_these_clinical_events(
        sickle_cell_disease_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    permanant_immunosuppression=patients.with_these_clinical_events(
        permanent_immunosuppression_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    temporary_immunosuppression=patients.with_these_clinical_events(
        temporary_immunosuppression_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    #
    psychosis_schiz_bipolar=patients.with_these_clinical_events(
        psychosis_schizophrenia_bipolar_affective_disease_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),
    ssri=patients.with_these_medications(
        ssri_codes, 
        between=["2019-12-01", campaign_start],
        returning="binary_flag", 
        return_expectations={"incidence": 0.01,},
    ),

    # https://github.com/opensafely/codelist-development/issues/4
    asplenia=patients.with_these_clinical_events(
        asplenia_codes,
        on_or_before=campaign_start,
        returning="binary_flag",
        return_expectations={"incidence": 0.01,},
    ),

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
                "latest": "2021-01-31",
            },
                "incidence":0.4
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
                "latest": latest_date,
            },
                "incidence": 0.1
        },
    ),
    # COVID VACCINATION - Pfizer BioNTech
    covid_vacc_pfizer_date=patients.with_tpp_vaccination_record(
        product_name_matches="COVID-19 mRNA Vac BNT162b2 30mcg/0.3ml conc for susp for inj multidose vials (Pfizer-BioNTech)",
        on_or_after="2020-12-01",  # check all december to date
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-08",  # first vaccine administered on the 8/12
                "latest": latest_date,},
            "incidence": 0.3
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
                "latest": latest_date,
            },
            "incidence": 0.1
        },
    ),

    # EPI-PEN
    adrenaline_pen=patients.with_these_medications(
        adrenaline_pen,
        on_or_after="2018-12-01",  # look for last two years
        returning="binary_flag",
        return_last_date_in_period=False,
        include_month=False,
        return_expectations={
            "date": {"earliest": "2018-12-01", "latest": latest_date},
            "incidence": 0.001,
        },
    ),
)
