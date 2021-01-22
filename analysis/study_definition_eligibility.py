# Import functions
##This study definitition is not currently in use



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


# Specifiy study defeinition

study = StudyDefinition(
    # Configure the expectations framework
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.2,
    },
    # This line defines the study population
    population=patients.satisfying(
        """
        has_follow_up AND
        (
        (age >=80 AND age <= 110) 
        OR
        (care_home_type != "U") 
        )      """,
        has_follow_up=patients.registered_with_one_practice_between(
        start_date="2019-12-01", 
        end_date="2020-12-07",
        return_expectations={"incidence": 0.90}
        ),
    ),
    # Demographic information
    age=patients.age_as_of(
        "2020-12-07",  # day before vaccine campaign start
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
    ageband=patients.categorised_as(
        {
            "0": "DEFAULT",
            "0-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >=  20 AND age < 30""",
            "30-39": """ age >=  30 AND age < 40""",
            "40-49": """ age >=  40 AND age < 50""",
            "50-59": """ age >=  50 AND age < 60""",
            "60-69": """ age >=  60 AND age < 70""",
            "70-79": """ age >=  70 AND age < 80""",
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
        include_date_of_match=True,
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
        include_date_of_match=True,
        return_expectations={
            "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
            "incidence": 0.75,
        },
    ),
    # NHS administrative region
    region=patients.registered_practice_as_of(
        "2020-12-07",
        returning="nuts1_region_name",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.1,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.2,
                    "South East": 0.2,
                },
            },
        },
    ),
    # CAREHOME STATUS
    care_home_type=patients.care_home_status_as_of(
        "2020-12-07",
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
            "U": "DEFAULT",
        },
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"PC": 0.05, "PN": 0.05, "PS": 0.05, "U": 0.85,},},
        },
    ),
)
