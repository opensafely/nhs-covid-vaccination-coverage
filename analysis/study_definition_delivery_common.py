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
        age>=16 AND age <= 120
        AND (
            covid_vacc_date
            OR
            (age >=50) 
            OR
            shielded
            OR
            (care_home)
            OR
            (LD)
        )
        """
    ),

    has_follow_up=patients.registered_with_one_practice_between(
        start_date="index_date - 12 months",
        end_date=index_date,
        return_expectations={"incidence": 0.90},
    ),
    registered=patients.registered_as_of(
        index_date, 
        return_expectations={"incidence": 0.98},
    ),
    has_died=patients.died_from_any_cause(
        on_or_before=index_date,
        returning="binary_flag",
        return_expectations={"incidence": 0.05},
    ),

    
    ### PRIMIS care home flag 
    care_home = patients.with_these_clinical_events(
        care_home_snomed_codes,
        return_expectations={"incidence": 0.15,}
    ),
    

    # Demographic information
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
            "16-29": """ age >= 16 AND age < 30""",
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
    # age bands for patients not in care homes (ie living in the community)
    # this is used to define eligible groups not defined by clinical criteria
    ageband_community=patients.categorised_as(
        {
            "care home" : "DEFAULT",
            "16-29": """ age >= 16 AND age < 30 AND NOT care_home""",
            "30-39": """ age >= 30 AND age < 40 AND NOT care_home""",
            "40-49": """ age >= 40 AND age < 50 AND NOT care_home""",
            "50-59": """ age >= 50 AND age < 60 AND NOT care_home""",
            "60-64": """ age >= 60 AND age < 65 AND NOT care_home""",
            "65-69": """ age >= 65 AND age < 70 AND NOT care_home""",
            "70-79": """ age >= 70 AND age < 80 AND NOT care_home""",
            "80+": """ age >=  80 AND age < 120 AND NOT care_home""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "care home":0.125,
                    "16-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-64": 0.0625,
                    "65-69": 0.0625,
                    "70-79": 0.125,
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
            "16-29": """ age >= 16 AND age < 30 """,
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
                    "0":0.0625,
                    "0-15": 0.0625,
                    "16-29": 0.0625,
                    "30-34": 0.0625,
                    "35-39": 0.0625,
                    "40-44": 0.0625,
                    "45-49": 0.0625,
                    "50-54": 0.0625,
                    "55-59": 0.0625,
                    "60-64": 0.0625,
                    "65-69": 0.0625,
                    "70-74": 0.0625,
                    "75-79": 0.0625,
                    "80-84": 0.0625,
                    "85-89": 0.0625,
                    "90+": 0.0625
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
    stp=patients.registered_practice_as_of(
        index_date,
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
    adrenaline_pen=patients.with_these_medications(
        adrenaline_pen,
        on_or_after="index_date - 24 months",  # look for last two years
        returning="binary_flag",
        return_last_date_in_period=False,
        include_month=False,
        return_expectations={
            "date": {"earliest": "2018-12-01", "latest": index_date},
            "incidence": 0.001,
        },
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
                
    LD = patients.with_these_clinical_events(
            wider_ld_codes, 
            return_expectations={"incidence": 0.02,},
    ),
            
)
