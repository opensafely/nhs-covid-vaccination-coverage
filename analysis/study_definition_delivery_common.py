from cohortextractor import patients, combine_codelists
from codelists import *
from datetime import date


campaign_start = "2020-12-07"
index_date = date.today().isoformat()


common_variables = dict(
    # Configure the expectations framework
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": index_date},
        "rate": "uniform",
        "incidence": 0.2,
    },

    # This line defines the study population
    population=patients.satisfying(
        """
        registered = 1
        AND
        NOT has_died
        AND 
        age <= 120
        AND 
        age>=16
        """,
        registered=patients.registered_as_of(
            index_date, 
        ),
        has_died=patients.died_from_any_cause(
            on_or_before=index_date,
            returning="binary_flag",
        ),
    ),

    has_follow_up=patients.registered_with_one_practice_between(
        start_date="index_date - 12 months",
        end_date=index_date,
        return_expectations={"incidence": 0.90},
    ),
    

    
    ### PRIMIS care home flag 
    care_home = patients.with_these_clinical_events(
        care_home_snomed_codes,
        return_expectations={"incidence": 0.15,}
    ),
    

    # Demographic information
    age=patients.age_as_of(
        "2021-08-31",  # PHE defined date for vaccine coverage
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
    ageband=patients.categorised_as(
        {
            "0": "DEFAULT",
            "16-29": """ age >= 16 AND age < 30""",
            "30-39": """ age >= 30 AND age < 40""",
            "40-49": """ age >= 40 AND age < 50""",
            "50-59": """ age >= 50 AND age < 60""",
            "60-69": """ age >= 60 AND age < 70""",
            "70-79": """ age >= 70 AND age < 80""",
            "80+": """ age >=  80 AND age < 120""",  
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "16-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.25,
                    "80+": 0.125,
                }
            },
        },
    ),
    
        # 5 year age bands
    ageband_5yr=patients.categorised_as(
        {
            "0" : "DEFAULT",
            "0-15": """ age >= 0 AND age < 16 """,
            "16-17": """ age >= 16 AND age < 18 """,
            "18-29": """ age >= 18 AND age < 30 """,
            "30-34": """ age >= 30 AND age < 35 """,
            "35-39": """ age >= 35 AND age < 40 """,
            "40-44": """ age >= 40 AND age < 45 """,
            "45-49": """ age >= 45 AND age < 50 """,
            "50-54": """ age >= 50 AND age < 55 """,
            "55-59": """ age >= 55 AND age < 60 """,
            "60-64": """ age >= 60 AND age < 65 """,
            "65-69": """ age >= 65 AND age < 70 """,
            "70-74": """ age >= 70 AND age < 75 """,
            "75-79": """ age >= 75 AND age < 80 """,
            "80-84": """ age >= 80 AND age < 85 """,
            "85-89": """ age >= 85 AND age < 90 """,
            "90+": """ age >=  90 AND age < 120 """,
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0":0.0125,
                    "0-15": 0.065,
                    "16-17": 0.065,
                    "18-29": 0.065,
                    "30-34": 0.065,
                    "35-39": 0.065,
                    "40-44": 0.065,
                    "45-49": 0.065,
                    "50-54": 0.065,
                    "55-59": 0.065,
                    "60-64": 0.065,
                    "65-69": 0.065,
                    "70-74": 0.065,
                    "75-79": 0.065,
                    "80-84": 0.065,
                    "85-89": 0.065,
                    "90+": 0.0125
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
    # practice pseudo id
    practice_id=patients.registered_practice_as_of(
        index_date, 
        returning="pseudo_id",
        return_expectations={
            "int": {"distribution": "normal", "mean": 1000, "stddev": 100},
            "incidence": 1,
        },
    ),
    # stp is an NHS administration region based on geography
#     stp=patients.registered_practice_as_of(
#         index_date,
#         returning="stp_code",
#         return_expectations={
#             "rate": "universal",
#             "category": {
#                 "ratios": {
#                     "STP1": 0.1,
#                     "STP2": 0.1,
#                     "STP3": 0.1,
#                     "STP4": 0.1,
#                     "STP5": 0.1,
#                     "STP6": 0.1,
#                     "STP7": 0.1,
#                     "STP8": 0.1,
#                     "STP9": 0.1,
#                     "STP10": 0.1,
#                 }
#             },
#         },
#     ),
    # NHS administrative region
    region=patients.registered_practice_as_of(
        index_date,
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
            index_date,
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
            on_or_after="index_date - 60 months",
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
            
    # Medications
    dmards=patients.with_these_medications(
        dmards_codes, 
        on_or_before=index_date,
        returning="binary_flag", 
        return_expectations={"incidence": 0.01,},
    ),
    ssri=patients.with_these_medications(
        ssri_codes, 
        between=["index_date - 12 months", index_date],
        returning="binary_flag", 
        return_expectations={"incidence": 0.01,},
    ),



    ### PRIMIS overall flag for shielded group
    shielded=patients.satisfying(
            """ severely_clinically_vulnerable
            AND NOT less_vulnerable""", 
        return_expectations={
            "incidence": 0.01,
                },

            ### SHIELDED GROUP - first flag all patients with "high risk" codes
        severely_clinically_vulnerable=patients.with_these_clinical_events(
            high_risk_codes, # note no date limits set
            find_last_match_in_period = True,
            return_expectations={"incidence": 0.02,},
        ),

        # find date at which the high risk code was added
        date_severely_clinically_vulnerable=patients.date_of(
            "severely_clinically_vulnerable", 
            date_format="YYYY-MM-DD",   
        ),

        ### NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
        less_vulnerable=patients.with_these_clinical_events(
            not_high_risk_codes, 
            on_or_after="date_severely_clinically_vulnerable",
            return_expectations={"incidence": 0.01,},
        ),
    ),
    
    
    # flag the newly expanded shielding group as of 15 feb (should be a subset of the previous flag)
    shielded_since_feb_15 = patients.satisfying(
            """severely_clinically_vulnerable_since_feb_15
                AND NOT new_shielding_status_reduced
                AND NOT previous_flag
            """,
        return_expectations={
            "incidence": 0.01,
                },
        
        ### SHIELDED GROUP - first flag all patients with "high risk" codes
        severely_clinically_vulnerable_since_feb_15=patients.with_these_clinical_events(
            high_risk_codes, 
            on_or_after= "2021-02-15",
            find_last_match_in_period = False,
            return_expectations={"incidence": 0.02,},
        ),

        # find date at which the high risk code was added
        date_vulnerable_since_feb_15=patients.date_of(
            "severely_clinically_vulnerable_since_feb_15", 
            date_format="YYYY-MM-DD",   
        ),

        ### check that patient's shielding status has not since been reduced to a lower risk level 
         # e.g. due to improved clinical condition of patient
        new_shielding_status_reduced=patients.with_these_clinical_events(
            not_high_risk_codes,
            on_or_after="date_vulnerable_since_feb_15",
            return_expectations={"incidence": 0.01,},
        ),
        
        # anyone with a previous flag of any risk level will not be added to the new shielding group
        previous_flag=patients.with_these_clinical_events(
            combine_codelists(high_risk_codes, not_high_risk_codes),
            on_or_before="2021-02-14",
            return_expectations={"incidence": 0.01,},
        ),
    ),

    # Chronic kidney disease flag
    # as per official COVID-19 vaccine reporting specification
    # IF CKD_COV_DAT <> NULL (diagnoses) | Select | Next
    # IF CKD15_DAT = NULL  (No stages)   | Reject | Next
    # IF CKD35_DAT>=CKD15_DAT            | Select | Reject
    # (i.e. any diagnostic code, or most recent stage recorded >=3)
    ckd = patients.satisfying(
        """ckd_cov_dat 
            OR
            ckd35_dat
        """,
        # Chronic kidney disease diagnostic codes
        ckd_cov_dat=patients.with_these_clinical_events(
            ckd_cov,
            returning="date",
            find_first_match_in_period=True,
            on_or_before="index_date",
            date_format="YYYY-MM-DD",
        ),
        # Chronic kidney disease codes - all stages
        ckd15_dat=patients.with_these_clinical_events(
            ckd15,
            returning="date",
            find_last_match_in_period=True,
            on_or_before="index_date",
            date_format="YYYY-MM-DD",
        ),
        # Chronic kidney disease codes-stages 3 - 5
        # only on or after latest CKD1-5 code
        ckd35_dat=patients.with_these_clinical_events(
            ckd35,
            returning="date",
            find_last_match_in_period=True,
            between=["ckd15_dat", "index_date"],
            date_format="YYYY-MM-DD",
        ),
    ),
        
    housebound = patients.satisfying(
            """housebound_date
                AND NOT no_longer_housebound
                AND NOT moved_into_care_home""",
        return_expectations={
            "incidence": 0.01,
                },
        
        housebound_date=patients.with_these_clinical_events( 
            housebound_codes, 
            on_or_before=index_date,
            find_last_match_in_period = True,
            returning="date",
            date_format="YYYY-MM-DD",
        ),   
        no_longer_housebound=patients.with_these_clinical_events( 
            no_longer_housebound_codes, 
            on_or_after="housebound_date",
        ),
        moved_into_care_home=patients.with_these_clinical_events(
            care_home_snomed_codes,
            on_or_after="housebound_date",
        ),
        
    ),
        
                
    LD = patients.with_these_clinical_events(
            wider_ld_codes, 
            return_expectations={"incidence": 0.02,},
    ),

    # declined vaccination / vaccination course / first dose (not including declined second dose)
    covid_vacc_declined_date = patients.with_these_clinical_events(
        covid_vacc_declined,
        returning="date",
        find_first_match_in_period=True,
        date_format = "YYYY-MM-DD",
        return_expectations={
            "date": {
                "earliest": "2020-12-08",  # first vaccine administered on the 8/12
                "latest": index_date,
            },
                "incidence":0.04
        },
    ),
            
)
