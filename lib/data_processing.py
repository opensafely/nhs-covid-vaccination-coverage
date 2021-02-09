""" This module cleans the patient-level data containing COVID vaccination dates and other relevant information"""

# Import statements
import pandas as pd
import numpy as np
import os

# Errors
from errors import DataCleaningError



def load_data(input_file='input_delivery.csv', input_path="output"):
    """
    This reads in a csv that must be in output/ directory and cleans the
    data ready for use in the graphs and tables

    Args:
        input_file (str): name of the input file. Default value is `input_delivery.csv'
                          The csv should contain one-row-per-patient, 
                          with columns representing various outcomes (covid vaccine dates),
                          demographics and clinical flags
        input_path (str): folder in which to find the input file
        
    Returns:
        Dataframe (df): Process dataframe


    Raises:
        DataCleaningError: If unable to complete any of the data loading or cleaning 
            processes

    """

    # import data and fill nulls with 0
    df = pd.read_csv(os.path.join("..",input_path, input_file)).fillna(0)

    # convert ethnic categories to words. There are 2 ways of categorising - into 
    # 6 groups or into 16 groups. 
    # this creates a new column called `ethnicity_6_groups`
    df = map_ethnicity(df, columnname="ethnicity", number_of_groups=6)

    # this creates a new column called `ethnicity_16_groups`
    df = map_ethnicity(df, columnname="ethnicity_16", number_of_groups=16)

    # describe imd partially in words and make new column called `imd_categories` from `imd`
    imd_lookup = {0:"Unknown", 1:"1 Most deprived", 2:"2", 3:"3", 4:"4", 5:"5 Least deprived"}
    for level, category in imd_lookup.items():
        df.loc[df["imd"] == level, "imd_categories"] = category
    df["imd_categories"].fillna("Unknown")

    # Assign vaccine status
    df = df.assign(
        covid_vacc_flag = np.where(df["covid_vacc_date"]!=0,"vaccinated","unvaccinated"),
        covid_vacc_flag_ox = np.where(df["covid_vacc_oxford_date"]!=0, 1, 0),
        covid_vacc_flag_pfz = np.where(df["covid_vacc_pfizer_date"]!=0, 1, 0),
        covid_vacc_2nd = np.where(df["covid_vacc_second_dose_date"]!=0, 1, 0),
        covid_vacc_bin = np.where(df["covid_vacc_date"]!=0, 1, 0))


    # Assign column SSRI to be where has SSRI and no psychosis/bipolar/schizophrenia/dementia or LD
    df = df.assign(
        ssri = np.where((df["ssri"]==1) & (df["psychosis_schiz_bipolar"]==0) &\
                    (df["intel_dis_incl_downs_syndrome"]==0) & (df["dementia"]==0), 1, 0))

    # Replace a region and STP with a value `0` with Unknown
    df = df.assign(
        region = df['region'].replace(0, "Unknown"),
        stp = df['stp'].replace(0, "Unknown"))

    # Replace `I` or `U` for sex with `Other/Unknown`
    df = df.assign(
        sex = df['sex'].replace(['I','U'], "Other/Unknown"))

    # categorise BMI into obese (i.e. BMI >=30) or non-obese (<30)
    df = df.assign(bmi = np.where((df["bmi"]=="Not obese"), "under 30", "30+"))

    # drop unnecssary columns or columns created for processing 
    df = df.drop(["imd","ethnicity_16", "ethnicity", "adrenaline_pen", "has_died", "has_follow_up"], 1)

    # care homes: regroup age bands (to later keep only 65+ labelled as care home residents)
    df.loc[(df["care_home_type"].isin(["PS","PN","PC"])) & (df["age"]>=65) & (df["age"]<70), "ageband"] = "65-69"

    # amend community age band to remove any care home flags for under 65s 
    #(only elderly care homes are included so these are likely live-in staff+their families or other non-care recipients)
    df.loc[(df["ageband_community"]=="care home") & (df["age"]<65), "ageband_community"] = df["ageband"]

    # for each specific situation or condition, replace 1 with YES and 0 with no. This makes the graphs easier to read
    for c in ["care_home","dementia", 
          "chronic_cardiac_disease", "current_copd", "dialysis", "dmards","psychosis_schiz_bipolar",
         "solid_organ_transplantation", "chemo_or_radio", "intel_dis_incl_downs_syndrome","ssri",
          "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer", "bone_marrow_transplant",
          "cystic_fibrosis", "sickle_cell_disease", "permanant_immunosuppression",
          "temporary_immunosuppression", "asplenia"]:
          df[c] = np.where(df[c]==1, "yes", "no")

    # rename columns for IMD and ageband for readability
    df = df.rename(columns={"imd":"Index_of_Multiple_Deprivation", "ageband_community":"community_ageband"})

    # get total population sizes and names for each STP
    stps = pd.read_csv(os.path.join("..","lib","stp_dict.csv"), usecols=["stp_id","name","list_size_o80"])
    df = df.merge(stps, left_on="stp", right_on="stp_id", how="left").drop(["care_home_type","age","stp_id"], 1).rename(columns={"name":"stp_name"})  

    return df




def map_ethnicity(df, columnname, number_of_groups):
    """
    This maps the numerical value in the dataframe to the ethnicity categories. It creates
    a new column called ethnicity_(number_of_groups)_groups. For example, ethnicity_6_groups.

    Args: 
        df (Dataframe): your dataframe of interest, 
                        with one row per patient where at least one column (columnname) contains an ethnicity code
        columnname (str): name of column containing ethnicity codes (with range 0-5 or 0-15)
        number_of_groups (int): Either 6 or 16

    Returns:
        Dataframe (df): Processed dataframe with a column added containing the name for each ethnicity category
    """

    if number_of_groups == 6:
        ethnicity_dict = {0:"Unknown", 1:"White", 2:"Mixed", 3:"South Asian", 4:"Black", 5:"Other"}
    elif number_of_groups == 16:
        ethnicity_lookup = pd.read_csv(os.path.join("..", "analysis", "ethnicity_16_lookup.csv")).to_dict('index')
        ethnicity_dict = {0:"Unknown"}
        for row, data in ethnicity_lookup.items():
            ethnicity_dict[(int(data["code"]))] = data["name"]
    else:
        raise DataCleaningError(message="You have provided a non-supported number of categories (only 6 or 16 are supported)")

    new_ethnicity_column_name = f"ethnicity_{number_of_groups}_groups"
    df[new_ethnicity_column_name] = [ethnicity_dict[x] for x in df[columnname].fillna(0).astype(int)]

    return df


