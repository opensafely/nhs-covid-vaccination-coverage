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
        age < 16
        AND 
        age >= 5
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
    # Demographic information
    age=patients.age_as_of(
        index_date,  # "2022-08-31",  # PHE defined date for vaccine coverage
        return_expectations={
            # "rate": "universal",
            "int": {"distribution": "normal", "mean": 10, "stddev": 1.5},
            # "int": {"distribution": "population_ages"},
        },
    ),
    ageband=patients.categorised_as(
        {
            "0": "DEFAULT",
            "5-11": """ age >= 5 AND age < 12""",
            "12-15": """ age >= 12 AND age < 16""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "5-11": 0.65,
                    "12-15": 0.35,
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
            "1": "index_of_multiple_deprivation >= 0 AND index_of_multiple_deprivation < 32844*1/5",
            "2": "index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5",
            "3": "index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5",
            "4": "index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5",
            "5": "index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation <= 32844",
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
            on_or_after="index_date - 60 months", minimum_age_at_measurement=16
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
    LD=patients.with_these_clinical_events(
        wider_ld_codes,
        return_expectations={
            "incidence": 0.02,
        },
    ),
)
