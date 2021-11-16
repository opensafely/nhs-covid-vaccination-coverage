""" This module cleans the patient-level data containing COVID vaccination dates and other relevant information"""

# Import statements
import pandas as pd
import numpy as np
import os

# Errors
from errors import DataCleaningError



def load_data(input_file='input_delivery.csv.gz', input_path="output"):
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
    df = pd.read_csv(os.path.join("..",input_path, input_file), compression='gzip').fillna(0)

    # fill unknown ethnicity from GP records with ethnicity from SUS (secondary care)
    df.loc[df["ethnicity"]==0, "ethnicity"] = df["ethnicity_6_sus"]
    df.loc[df["ethnicity_16"]==0, "ethnicity_16"] = df["ethnicity_16_sus"]
    
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
        covid_vacc_flag_mod = np.where(df["covid_vacc_moderna_date"]!=0, 1, 0),
        covid_vacc_2nd = np.where(df["covid_vacc_second_dose_date"]!=0, 1, 0),
        covid_vacc_3rd = np.where(df["covid_vacc_third_dose_date"]!=0, 1, 0),
        covid_vacc_bin = np.where(df["covid_vacc_date"]!=0, 1, 0))
    
    
    # Create a single field for brand of first and second dose
    # This excludes any uncertain cases where date of brand was too early or multiple brands were recorded
    choices = ["Oxford-AZ", "Pfizer", "Moderna", "Unknown"]
    doses = {"first":"covid_vacc_date", "second":"covid_vacc_second_dose_date"}
    for dose, field_name in doses.items():
        conditions = [( # pt has had an oxford vaccine, on or after the date this brand was first administered 
                        # in UK (minus 1 day; if date is unfeasible, vaccine type may be incorrect):
                        df["covid_vacc_oxford_date"].astype(str)>="2020-01-03") & ( 
                       # oxford vaccine was on date of selected dose:
                       df["covid_vacc_oxford_date"]==df[field_name]) & ( 
                        # oxford vaccine was not on same date as another brand:
                       df["covid_vacc_oxford_date"]!=df["covid_vacc_pfizer_date"]) & ( 
                       df["covid_vacc_oxford_date"]!=df["covid_vacc_moderna_date"]),
                        ## repeat for pfizer and moderna:
                      (df["covid_vacc_pfizer_date"].astype(str)>="2020-12-07") & (
                       df["covid_vacc_pfizer_date"]==df[field_name]) & (   
                       df["covid_vacc_pfizer_date"]!=df["covid_vacc_oxford_date"]) & (
                       df["covid_vacc_pfizer_date"]!=df["covid_vacc_moderna_date"]),
                      # moderna - only include if dose date is after the date first administered in UK
                      (df["covid_vacc_moderna_date"].astype(str)>="2021-04-06") & (
                       df["covid_vacc_moderna_date"]==df[field_name]) & (   
                       df["covid_vacc_moderna_date"]!=df["covid_vacc_oxford_date"]) & (
                       df["covid_vacc_moderna_date"]!=df["covid_vacc_pfizer_date"]),
                       ## unknown type - pt has had the dose but the above conditions do not apply
                        # these may be unspecified brands or where two diff brands were recorded same day
                       df[field_name]!=0
        ]
    
        df[f'brand_of_{dose}_dose'] = np.select(conditions, choices, default="none")
 
    # Mixed doses:
    # flag patients with different brands for the first and second dose 
    df = df.assign(    
        covid_vacc_ox_pfz = np.where(
                                      ((df['brand_of_first_dose']=="Oxford-AZ") & (df['brand_of_second_dose']=="Pfizer")) | (
                                       (df['brand_of_first_dose']=="Pfizer") & (df['brand_of_second_dose']=="Oxford-AZ")), 1, 0),
        covid_vacc_ox_mod = np.where(
                                      ((df['brand_of_first_dose']=="Oxford-AZ") & (df['brand_of_second_dose']=="Moderna")) | (
                                       (df['brand_of_first_dose']=="Moderna") & (df['brand_of_second_dose']=="Oxford-AZ")), 1, 0),
        covid_vacc_mod_pfz = np.where(
                                      ((df['brand_of_first_dose']=="Moderna") & (df['brand_of_second_dose']=="Pfizer")) | (
                                       (df['brand_of_first_dose']=="Pfizer") & (df["brand_of_second_dose"]=="Moderna")), 1, 0),
        )
        
    # declined - suppress if vaccine has been received
    df["covid_vacc_declined_date"] = np.where(df["covid_vacc_date"]==0, df["covid_vacc_declined_date"], 0)
    
    # create an additional field for 2nd dose to use as a flag for each eligible group
    df["2nd_dose"] = df["covid_vacc_2nd"]
    
    # Assign column SSRI to be where has SSRI and no psychosis/bipolar/schizophrenia/dementia or LD
    df = df.assign(
        ssri = np.where((df["ssri"]==1) & (df["psychosis_schiz_bipolar"]==0) &\
                    (df["LD"]==0) & (df["dementia"]==0), 1, 0))

    # Replace a region and STP with a value `0` with Unknown
    df = df.assign(
        region = df['region'].replace(0, "Unknown"),
        stp = df['stp'].replace(0, "Unknown"))

    # Replace `I` or `U` for sex with `Other/Unknown`
    df = df.assign(
        sex = df['sex'].replace(['I','U'], "Other/Unknown"))

    # categorise BMI into obese (i.e. BMI >=30) or non-obese (<30)
    df = df.assign(bmi = np.where((df["bmi"]=="Not obese"), "under 30", "30+"))

    # drop unnecessary columns or columns created for processing 
    df = df.drop(["imd","ethnicity_16", "ethnicity", 'ethnicity_6_sus',
       'ethnicity_16_sus', "has_follow_up"], 1)

    # categorise into priority groups (similar to the national groups but not exactly the same)
    conditions = [
        (df["care_home"]==1) & (df["age"]>=65),
        (df["age"]>=80),
        (df["age"]>=70),
        (df["shielded"]==1),
        (df["age"]>=65),
        (df["LD"]==1),
        (df["age"]>=60),
        (df["age"]>=55),
        (df["age"]>=50),
        (df["age"]>=40),
        (df["age"]>=30),
        (df["age"]>=18)]
    choices = [3,1,2,4,5,6,7,8,9,10,11,12]
    # note the numbers here denote the desired sort order in which we want to look at these groups, not the priority order
    
    # create field "priority_group" which uses the appropriate value from `choices` according to the `conditions` met by each line of data. If none are met, assigns 0.
    # Eg. for patient aged 71 but not in a care home, patient does not meet the first or second criteria, but meets the third so is assigned to the third of the `choices` i.e. `2`.
    df['priority_group'] = np.select(conditions, choices, default=0)

    # group into broad priority groups vs others
    df["priority_status"] = np.where((df["priority_group"]>0)&(df["priority_group"]<10), "Priority groups", "Others")
    
    # rename column for clarity
    df = df.rename(columns={"shielded_since_feb_15":"newly_shielded_since_feb_15"})
    
    # for each specific situation or condition, replace 1 with YES and 0 with no. This makes the graphs easier to read
    for c in ["2nd_dose", "LD", "newly_shielded_since_feb_15", "dementia", 
          "chronic_cardiac_disease", "current_copd", "dialysis", "dmards","psychosis_schiz_bipolar",
         "solid_organ_transplantation", "chemo_or_radio", "intel_dis_incl_downs_syndrome","ssri",
          "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer", "housebound"]:
          df[c] = np.where(df[c]==1, "yes", "no")


    # get total population sizes and names for each STP
    stps = pd.read_csv(os.path.join("..","lib","stp_dict.csv"), usecols=["stp_id","name","list_size_o80"])
    df = df.merge(stps, left_on="stp", right_on="stp_id", how="left").rename(columns={"name":"stp_name"})
    
    # drop additional columns
    df = df.drop(['care_home', 'age',"stp_id"], 1)  

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


